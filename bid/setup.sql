-- 규격대조 저장 테이블 (워크노트와 같은 Supabase 프로젝트, 본인 데이터만 보임)
create table if not exists public.bid_items (
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  id text not null,
  kind text not null,
  data jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);
alter table public.bid_items enable row level security;
drop policy if exists "bid_items own rows" on public.bid_items;
create policy "bid_items own rows" on public.bid_items
  for all to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());
grant select, insert, update, delete on public.bid_items to authenticated;
