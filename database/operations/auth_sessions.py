from database.db import engine, text


def create_auth_session(
    user_id: int,
    token_hash: str,
    device_name: str | None,
    ip_address: str | None,
    user_agent: str | None,
    expires_at,
):
    query = text("""
        INSERT INTO auth_sessions (
            user_id,
            token_hash,
            device_name,
            ip_address,
            user_agent,
            expires_at
        )
        VALUES (
            :user_id,
            :token_hash,
            :device_name,
            :ip_address,
            :user_agent,
            :expires_at
        )
        RETURNING session_id
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {
            "user_id": user_id,
            "token_hash": token_hash,
            "device_name": device_name,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": expires_at,
        })

        return result.scalar_one()

def get_auth_session(token_hash: str):
    query = text("""
        SELECT
            session_id,
            user_id,
            expires_at,
            revoked_at
        FROM auth_sessions
        WHERE token_hash = :token_hash
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {
            "token_hash": token_hash
        })

        return result.fetchone()

def update_session_last_used(session_id: int):
    query = text("""
        UPDATE auth_sessions
        SET last_used_at = CURRENT_TIMESTAMP
        WHERE session_id = :session_id
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "session_id": session_id
        })
def revoke_auth_session(session_id: int):
    query = text("""
        UPDATE auth_sessions
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE session_id = :session_id
          AND revoked_at IS NULL
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "session_id": session_id
        })