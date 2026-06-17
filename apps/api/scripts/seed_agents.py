from app.db.session import SessionLocal
from app.seeds.agents import seed_default_agents


def main() -> None:
    with SessionLocal() as db:
        inserted_count = seed_default_agents(db)

    print(f"Seeded {inserted_count} default agents.")


if __name__ == "__main__":
    main()
