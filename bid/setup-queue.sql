-- 회사 네트워크 우회용 AI 작업 목록 (브라우저는 저장 주소로만 통신하고, AI 함수는 서버 안에서 실행된다)
create extension if not exists pg_net;

create table if not exists public.bid_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  status text not null default 'queued',
  request jsonb not null,
  result jsonb,
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.bid_jobs enable row level security;
drop policy if exists "bid_jobs own rows" on public.bid_jobs;
create policy "bid_jobs own rows" on public.bid_jobs
  for all to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());
grant select, insert, delete on public.bid_jobs to authenticated;

-- 작업이 들어오면 서버에서 bid-ai 함수를 깨운다
create or replace function public.bid_jobs_kick() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url := 'https://kvddqnhabvdegmllswsi.supabase.co/functions/v1/bid-ai',
    body := jsonb_build_object('job_id', new.id),
    headers := '{"Content-Type": "application/json"}'::jsonb,
    timeout_milliseconds := 5000
  );
  return new;
end $$;
drop trigger if exists bid_jobs_kick on public.bid_jobs;
create trigger bid_jobs_kick after insert on public.bid_jobs
  for each row execute function public.bid_jobs_kick();

-- 하루 지난 작업은 지운다
delete from public.bid_jobs where created_at < now() - interval '1 day';
