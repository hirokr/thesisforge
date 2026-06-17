"""add row-level security policies

Revision ID: 20260617_0002
Revises: 20260617_0001
Create Date: 2026-06-17
"""
from collections.abc import Sequence

from alembic import op

revision: str = "20260617_0002"
down_revision: str | None = "20260617_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_DATA_TABLES = [
    "user_profiles",
    "thesis_projects",
    "documents",
    "document_chunks",
    "references",
    "analysis_runs",
    "agent_messages",
    "agent_findings",
    "citation_checks",
    "reports",
    "action_tasks",
    "supervisor_feedback",
    "audit_logs",
]

OWNERSHIP_TRIGGER_TABLES = {
    "thesis_projects": ["owner_id"],
    "documents": ["project_id"],
    "document_chunks": ["document_id"],
    "references": ["project_id", "document_id"],
    "analysis_runs": ["project_id"],
    "agent_messages": ["analysis_run_id"],
    "agent_findings": ["analysis_run_id"],
    "citation_checks": ["analysis_run_id", "reference_id"],
    "reports": ["project_id", "analysis_run_id"],
    "action_tasks": ["project_id", "finding_id"],
    "supervisor_feedback": ["project_id"],
}


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.current_thesisforge_profile_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        AS $$
            SELECT id
            FROM public.user_profiles
            WHERE auth_user_id = auth.uid()::text
            LIMIT 1
        $$;

        CREATE OR REPLACE FUNCTION public.prevent_thesisforge_ownership_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            column_name text;
        BEGIN
            FOREACH column_name IN ARRAY TG_ARGV LOOP
                IF to_jsonb(OLD) -> column_name IS DISTINCT FROM to_jsonb(NEW) -> column_name THEN
                    RAISE EXCEPTION 'Ownership fields cannot be changed';
                END IF;
            END LOOP;
            RETURN NEW;
        END;
        $$;

        CREATE OR REPLACE FUNCTION public.can_access_project(project_uuid uuid)
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT EXISTS (
                SELECT 1
                FROM public.thesis_projects project
                WHERE project.id = project_uuid
                AND project.owner_id = public.current_thesisforge_profile_id()
            )
        $$;

        CREATE OR REPLACE FUNCTION public.can_access_document(document_uuid uuid)
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT EXISTS (
                SELECT 1
                FROM public.documents document
                JOIN public.thesis_projects project ON project.id = document.project_id
                WHERE document.id = document_uuid
                AND project.owner_id = public.current_thesisforge_profile_id()
            )
        $$;

        CREATE OR REPLACE FUNCTION public.can_access_analysis_run(run_uuid uuid)
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT EXISTS (
                SELECT 1
                FROM public.analysis_runs run
                JOIN public.thesis_projects project ON project.id = run.project_id
                WHERE run.id = run_uuid
                AND project.owner_id = public.current_thesisforge_profile_id()
            )
        $$;

        CREATE OR REPLACE FUNCTION public.can_access_reference(reference_uuid uuid)
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT EXISTS (
                SELECT 1
                FROM public.references reference
                JOIN public.thesis_projects project ON project.id = reference.project_id
                WHERE reference.id = reference_uuid
                AND project.owner_id = public.current_thesisforge_profile_id()
            )
        $$;
        """
    )

    for table_name in USER_DATA_TABLES:
        op.execute(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY user_profiles_own_select ON public.user_profiles
            FOR SELECT USING (auth_user_id = auth.uid()::text);
        CREATE POLICY user_profiles_own_insert ON public.user_profiles
            FOR INSERT WITH CHECK (auth_user_id = auth.uid()::text AND role <> 'admin');
        CREATE POLICY user_profiles_own_update ON public.user_profiles
            FOR UPDATE USING (auth_user_id = auth.uid()::text)
            WITH CHECK (auth_user_id = auth.uid()::text AND role <> 'admin');

        CREATE POLICY thesis_projects_owner_select ON public.thesis_projects
            FOR SELECT USING (owner_id = public.current_thesisforge_profile_id());
        CREATE POLICY thesis_projects_owner_insert ON public.thesis_projects
            FOR INSERT WITH CHECK (owner_id = public.current_thesisforge_profile_id());
        CREATE POLICY thesis_projects_owner_update ON public.thesis_projects
            FOR UPDATE USING (owner_id = public.current_thesisforge_profile_id())
            WITH CHECK (owner_id = public.current_thesisforge_profile_id());
        CREATE POLICY thesis_projects_owner_delete ON public.thesis_projects
            FOR DELETE USING (owner_id = public.current_thesisforge_profile_id());

        CREATE POLICY documents_project_owner_select ON public.documents
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY documents_project_owner_insert ON public.documents
            FOR INSERT WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY documents_project_owner_update ON public.documents
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY documents_project_owner_delete ON public.documents
            FOR DELETE USING (public.can_access_project(project_id));

        CREATE POLICY document_chunks_project_owner_select ON public.document_chunks
            FOR SELECT USING (public.can_access_document(document_id));
        CREATE POLICY document_chunks_project_owner_insert ON public.document_chunks
            FOR INSERT WITH CHECK (public.can_access_document(document_id));
        CREATE POLICY document_chunks_project_owner_update ON public.document_chunks
            FOR UPDATE USING (public.can_access_document(document_id))
            WITH CHECK (public.can_access_document(document_id));
        CREATE POLICY document_chunks_project_owner_delete ON public.document_chunks
            FOR DELETE USING (public.can_access_document(document_id));

        CREATE POLICY references_project_owner_select ON public.references
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY references_project_owner_insert ON public.references
            FOR INSERT WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY references_project_owner_update ON public.references
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY references_project_owner_delete ON public.references
            FOR DELETE USING (public.can_access_project(project_id));

        CREATE POLICY analysis_runs_project_owner_select ON public.analysis_runs
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY analysis_runs_project_owner_insert ON public.analysis_runs
            FOR INSERT WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY analysis_runs_project_owner_update ON public.analysis_runs
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY analysis_runs_project_owner_delete ON public.analysis_runs
            FOR DELETE USING (public.can_access_project(project_id));

        CREATE POLICY agent_messages_project_owner_select ON public.agent_messages
            FOR SELECT USING (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_messages_project_owner_insert ON public.agent_messages
            FOR INSERT WITH CHECK (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_messages_project_owner_update ON public.agent_messages
            FOR UPDATE USING (public.can_access_analysis_run(analysis_run_id))
            WITH CHECK (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_messages_project_owner_delete ON public.agent_messages
            FOR DELETE USING (public.can_access_analysis_run(analysis_run_id));

        CREATE POLICY agent_findings_project_owner_select ON public.agent_findings
            FOR SELECT USING (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_findings_project_owner_insert ON public.agent_findings
            FOR INSERT WITH CHECK (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_findings_project_owner_update ON public.agent_findings
            FOR UPDATE USING (public.can_access_analysis_run(analysis_run_id))
            WITH CHECK (public.can_access_analysis_run(analysis_run_id));
        CREATE POLICY agent_findings_project_owner_delete ON public.agent_findings
            FOR DELETE USING (public.can_access_analysis_run(analysis_run_id));

        CREATE POLICY citation_checks_project_owner_select ON public.citation_checks
            FOR SELECT USING (
                public.can_access_analysis_run(analysis_run_id)
                AND (reference_id IS NULL OR public.can_access_reference(reference_id))
            );
        CREATE POLICY citation_checks_project_owner_insert ON public.citation_checks
            FOR INSERT WITH CHECK (
                public.can_access_analysis_run(analysis_run_id)
                AND (reference_id IS NULL OR public.can_access_reference(reference_id))
            );
        CREATE POLICY citation_checks_project_owner_update ON public.citation_checks
            FOR UPDATE USING (
                public.can_access_analysis_run(analysis_run_id)
                AND (reference_id IS NULL OR public.can_access_reference(reference_id))
            )
            WITH CHECK (
                public.can_access_analysis_run(analysis_run_id)
                AND (reference_id IS NULL OR public.can_access_reference(reference_id))
            );
        CREATE POLICY citation_checks_project_owner_delete ON public.citation_checks
            FOR DELETE USING (public.can_access_analysis_run(analysis_run_id));

        CREATE POLICY reports_project_owner_select ON public.reports
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY reports_project_owner_insert ON public.reports
            FOR INSERT WITH CHECK (
                public.can_access_project(project_id)
                AND (analysis_run_id IS NULL OR public.can_access_analysis_run(analysis_run_id))
            );
        CREATE POLICY reports_project_owner_update ON public.reports
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (
                public.can_access_project(project_id)
                AND (analysis_run_id IS NULL OR public.can_access_analysis_run(analysis_run_id))
            );
        CREATE POLICY reports_project_owner_delete ON public.reports
            FOR DELETE USING (public.can_access_project(project_id));

        CREATE POLICY action_tasks_project_owner_select ON public.action_tasks
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY action_tasks_project_owner_insert ON public.action_tasks
            FOR INSERT WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY action_tasks_project_owner_update ON public.action_tasks
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY action_tasks_project_owner_delete ON public.action_tasks
            FOR DELETE USING (public.can_access_project(project_id));

        CREATE POLICY supervisor_feedback_project_owner_select ON public.supervisor_feedback
            FOR SELECT USING (public.can_access_project(project_id));
        CREATE POLICY supervisor_feedback_project_owner_insert ON public.supervisor_feedback
            FOR INSERT WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY supervisor_feedback_project_owner_update ON public.supervisor_feedback
            FOR UPDATE USING (public.can_access_project(project_id))
            WITH CHECK (public.can_access_project(project_id));
        CREATE POLICY supervisor_feedback_project_owner_delete ON public.supervisor_feedback
            FOR DELETE USING (public.can_access_project(project_id));
        """
    )

    for table_name, column_names in OWNERSHIP_TRIGGER_TABLES.items():
        trigger_args = ", ".join(f"'{column_name}'" for column_name in column_names)
        op.execute(
            f"""
            CREATE TRIGGER prevent_{table_name}_ownership_update
            BEFORE UPDATE ON public.{table_name}
            FOR EACH ROW
            EXECUTE FUNCTION public.prevent_thesisforge_ownership_update({trigger_args})
            """
        )


def downgrade() -> None:
    for table_name in OWNERSHIP_TRIGGER_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS prevent_{table_name}_ownership_update ON public.{table_name}")

    op.execute(
        """
        DROP POLICY IF EXISTS supervisor_feedback_project_owner_delete ON public.supervisor_feedback;
        DROP POLICY IF EXISTS supervisor_feedback_project_owner_update ON public.supervisor_feedback;
        DROP POLICY IF EXISTS supervisor_feedback_project_owner_insert ON public.supervisor_feedback;
        DROP POLICY IF EXISTS supervisor_feedback_project_owner_select ON public.supervisor_feedback;
        DROP POLICY IF EXISTS action_tasks_project_owner_delete ON public.action_tasks;
        DROP POLICY IF EXISTS action_tasks_project_owner_update ON public.action_tasks;
        DROP POLICY IF EXISTS action_tasks_project_owner_insert ON public.action_tasks;
        DROP POLICY IF EXISTS action_tasks_project_owner_select ON public.action_tasks;
        DROP POLICY IF EXISTS reports_project_owner_delete ON public.reports;
        DROP POLICY IF EXISTS reports_project_owner_update ON public.reports;
        DROP POLICY IF EXISTS reports_project_owner_insert ON public.reports;
        DROP POLICY IF EXISTS reports_project_owner_select ON public.reports;
        DROP POLICY IF EXISTS citation_checks_project_owner_delete ON public.citation_checks;
        DROP POLICY IF EXISTS citation_checks_project_owner_update ON public.citation_checks;
        DROP POLICY IF EXISTS citation_checks_project_owner_insert ON public.citation_checks;
        DROP POLICY IF EXISTS citation_checks_project_owner_select ON public.citation_checks;
        DROP POLICY IF EXISTS agent_findings_project_owner_delete ON public.agent_findings;
        DROP POLICY IF EXISTS agent_findings_project_owner_update ON public.agent_findings;
        DROP POLICY IF EXISTS agent_findings_project_owner_insert ON public.agent_findings;
        DROP POLICY IF EXISTS agent_findings_project_owner_select ON public.agent_findings;
        DROP POLICY IF EXISTS agent_messages_project_owner_delete ON public.agent_messages;
        DROP POLICY IF EXISTS agent_messages_project_owner_update ON public.agent_messages;
        DROP POLICY IF EXISTS agent_messages_project_owner_insert ON public.agent_messages;
        DROP POLICY IF EXISTS agent_messages_project_owner_select ON public.agent_messages;
        DROP POLICY IF EXISTS analysis_runs_project_owner_delete ON public.analysis_runs;
        DROP POLICY IF EXISTS analysis_runs_project_owner_update ON public.analysis_runs;
        DROP POLICY IF EXISTS analysis_runs_project_owner_insert ON public.analysis_runs;
        DROP POLICY IF EXISTS analysis_runs_project_owner_select ON public.analysis_runs;
        DROP POLICY IF EXISTS references_project_owner_delete ON public.references;
        DROP POLICY IF EXISTS references_project_owner_update ON public.references;
        DROP POLICY IF EXISTS references_project_owner_insert ON public.references;
        DROP POLICY IF EXISTS references_project_owner_select ON public.references;
        DROP POLICY IF EXISTS document_chunks_project_owner_delete ON public.document_chunks;
        DROP POLICY IF EXISTS document_chunks_project_owner_update ON public.document_chunks;
        DROP POLICY IF EXISTS document_chunks_project_owner_insert ON public.document_chunks;
        DROP POLICY IF EXISTS document_chunks_project_owner_select ON public.document_chunks;
        DROP POLICY IF EXISTS documents_project_owner_delete ON public.documents;
        DROP POLICY IF EXISTS documents_project_owner_update ON public.documents;
        DROP POLICY IF EXISTS documents_project_owner_insert ON public.documents;
        DROP POLICY IF EXISTS documents_project_owner_select ON public.documents;
        DROP POLICY IF EXISTS thesis_projects_owner_delete ON public.thesis_projects;
        DROP POLICY IF EXISTS thesis_projects_owner_update ON public.thesis_projects;
        DROP POLICY IF EXISTS thesis_projects_owner_insert ON public.thesis_projects;
        DROP POLICY IF EXISTS thesis_projects_owner_select ON public.thesis_projects;
        DROP POLICY IF EXISTS user_profiles_own_update ON public.user_profiles;
        DROP POLICY IF EXISTS user_profiles_own_insert ON public.user_profiles;
        DROP POLICY IF EXISTS user_profiles_own_select ON public.user_profiles;
        """
    )

    for table_name in reversed(USER_DATA_TABLES):
        op.execute(f"ALTER TABLE public.{table_name} DISABLE ROW LEVEL SECURITY")

    op.execute(
        """
        DROP FUNCTION IF EXISTS public.can_access_reference(uuid);
        DROP FUNCTION IF EXISTS public.can_access_analysis_run(uuid);
        DROP FUNCTION IF EXISTS public.can_access_document(uuid);
        DROP FUNCTION IF EXISTS public.can_access_project(uuid);
        DROP FUNCTION IF EXISTS public.prevent_thesisforge_ownership_update();
        DROP FUNCTION IF EXISTS public.current_thesisforge_profile_id();
        """
    )
