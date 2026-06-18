import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

async function readSource(path) {
  return readFile(join(root, path), "utf8");
}

function assertIncludes(source, expected, context) {
  assert.ok(source.includes(expected), `${context} should include ${JSON.stringify(expected)}`);
}

function assertMatches(source, pattern, context) {
  assert.match(source, pattern, context);
}

async function smokeLoginPage() {
  const source = await readSource("src/app/login/page.tsx");

  assertIncludes(source, "export default function LoginPage", "login route");
  assertIncludes(source, "signInWithPassword", "login route");
  assertIncludes(source, "Email", "login form");
  assertIncludes(source, "Password", "login form");
  assertIncludes(source, "Invalid email or password.", "login error handling");
}

async function smokeDashboardPage() {
  const source = await readSource("src/app/dashboard/page.tsx");

  assertIncludes(source, "export default function DashboardPage", "dashboard route");
  assertIncludes(source, "listProjects", "dashboard data loading");
  assertIncludes(source, "Load demo project", "dashboard demo action");
  assertIncludes(source, "Create project", "dashboard create action");
  assertIncludes(source, "No projects yet", "dashboard empty state");
}

async function smokeCreateProjectPage() {
  const source = await readSource("src/app/projects/new/page.tsx");

  assertIncludes(source, "export default function CreateProjectPage", "create project route");
  assertIncludes(source, "createProject", "create project submission");
  assertIncludes(source, "Enter a thesis title.", "create project validation");
  assertIncludes(source, "Thesis title", "create project form");
  assertIncludes(source, "Create project", "create project action");
}

async function smokeReportPage() {
  const reportPage = await readSource("src/app/projects/[projectId]/reports/[reportId]/page.tsx");
  const scoreCards = await readSource("src/components/report/score-cards.tsx");
  const priorityFixes = await readSource("src/components/report/priority-fix-list.tsx");
  const defenseQuestions = await readSource("src/components/report/defense-questions-list.tsx");

  assertIncludes(reportPage, "export default function FinalReportPage", "report route");
  assertIncludes(reportPage, "getReport(reportId)", "report data loading");
  assertIncludes(reportPage, "OverallScoreCard", "report score component");
  assertIncludes(reportPage, "PriorityFixList", "report fixes component");
  assertIncludes(reportPage, "DefenseQuestionsList", "report defense component");
  assertIncludes(reportPage, "Copy report", "report copy action");
  assertIncludes(reportPage, "Download markdown", "report download action");
  assertIncludes(scoreCards, "Overall score", "score card mock coverage surface");
  assertMatches(priorityFixes, /priority_fixes/, "priority fix mock coverage surface");
  assertMatches(defenseQuestions, /defense_questions/, "defense question mock coverage surface");
}

await smokeLoginPage();
await smokeDashboardPage();
await smokeCreateProjectPage();
await smokeReportPage();

console.log("Frontend smoke checks passed: login, dashboard, create project, and report pages.");
