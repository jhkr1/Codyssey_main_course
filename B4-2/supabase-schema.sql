-- Supabase SQL Editor에서 한 번 실행하세요.
create table if not exists movies (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  director text not null,
  year integer,
  genre text not null,
  rating integer not null check (rating between 1 and 5),
  note text not null,
  created_at timestamptz not null default now()
);

alter table movies enable row level security;
create policy "public movie access" on movies for all using (true) with check (true);
