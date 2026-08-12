-- Orders table for the Order Status Voice Agent.
-- Order number is the primary lookup key, email is a fallback for
-- callers who do not have their order number handy. Store scopes an
-- order to one of the demo brands, so the same table and lookup logic
-- can serve more than one storefront.

create table if not exists public.orders (
    id uuid primary key default gen_random_uuid(),
    order_number text unique not null,
    email text not null,
    status text not null check (status in ('processing', 'shipped', 'delivered')),
    tracking_number text,
    carrier text,
    estimated_delivery date,
    store text not null check (store in ('Bondi & Co', 'Southbank Supply', 'Redgum Traders')),
    created_at timestamptz not null default now()
);

-- Case insensitive lookups are the common path for this table, since
-- callers read order numbers and emails out loud with inconsistent casing.
create index if not exists orders_order_number_lower_idx on public.orders (lower(order_number));
create index if not exists orders_email_lower_idx on public.orders (lower(email));
create index if not exists orders_store_idx on public.orders (store);

alter table public.orders enable row level security;

-- The voice agent's backend reads through a service role key, which
-- bypasses RLS by design. This policy exists so the table is not
-- silently unreadable if it is ever queried with an anon key instead.
create policy "Service role can read orders"
    on public.orders
    for select
    to service_role
    using (true);
