from database.db import engine, text


def get_or_create_model(provider: str, name: str):
    query = text("""
        INSERT INTO llm_models (
            provider,
            name
        )
        VALUES (
            :provider,
            :name
        )
        ON CONFLICT (provider, name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING model_id
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "provider": provider,
                "name": name,
            },
        )

        return result.scalar_one()