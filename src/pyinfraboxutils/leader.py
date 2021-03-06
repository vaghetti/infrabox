import os
import time
import sys
from pyinfraboxutils import get_logger

logger = get_logger('infrabox')

def _is_leader(conn, service_name):
    if os.environ.get('INFRABOX_DISABLE_LEADER_ELECTION', 'false') == 'true':
        return True

    conn.rollback()
    c = conn.cursor()
    c.execute("""
        INSERT INTO leader_election (service_name, last_seen_active)
        VALUES (%s, now())
        ON CONFLICT (service_name)
        DO UPDATE SET
            service_name = CASE WHEN leader_election.last_seen_active < now() - interval '30 second'
                        THEN EXCLUDED.service_name
                        ELSE leader_election.service_name
                        END,
            last_seen_active = CASE WHEN leader_election.service_name = EXCLUDED.service_name
                                    THEN EXCLUDED.last_seen_active
                                    ELSE leader_election.last_seen_active
                                    END
        RETURNING service_name = %s;
    """, [service_name, service_name])
    r = c.fetchone()
    c.close()
    conn.commit()
    return r[0]

def is_leader(conn, service_name):
    leader = _is_leader(conn, service_name)

    if not leader:
        logger.info('Not the leader anymore')
        sys.exit(1)

    return True

def elect_leader(conn, service_name):
    while True:
        leader = _is_leader(conn, service_name)
        if leader:
            logger.info("I'm the leader")
            return True
        else:
            logger.info("Not the leader, retrying")
            time.sleep(5)
