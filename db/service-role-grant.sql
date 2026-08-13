-- The service_role Postgres role bypasses row level security by
-- design, but it still needs base table privileges granted, RLS
-- policies alone are not enough. This was missed in the original
-- migration and cost real debugging time, recorded here so the
-- schema file and the actual database stay honest with each other.

grant select, insert, update, delete on public.orders to service_role;
