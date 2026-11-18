-- Esquema de la base de datos. Pégalo en Supabase → SQL Editor → Run (una sola vez).

-- Suscripción de cada usuario. Solo la escribe el webhook de Stripe (con la clave de servicio).
create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users (id) on delete cascade,
  stripe_customer_id text unique,
  stripe_subscription_id text unique,
  plan text,                                -- mensual | trimestral | anual
  status text not null default 'incomplete', -- estado de Stripe: active, trialing, past_due, canceled...
  current_period_end timestamptz,
  cancel_at_period_end boolean not null default false,
  updated_at timestamptz not null default now()
);

alter table public.subscriptions enable row level security;

drop policy if exists "ver mi suscripción" on public.subscriptions;
create policy "ver mi suscripción" on public.subscriptions
  for select using (auth.uid() = user_id);

-- Respuestas de los alumnos, para el progreso y el repaso de fallos.
create table if not exists public.attempts (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id) on delete cascade,
  question_id text not null,
  correct boolean not null,
  mode text not null default 'practica', -- practica | simulacro
  created_at timestamptz not null default now()
);

create index if not exists attempts_user_idx on public.attempts (user_id, created_at desc);

alter table public.attempts enable row level security;

drop policy if exists "ver mis respuestas" on public.attempts;
create policy "ver mis respuestas" on public.attempts
  for select using (auth.uid() = user_id);

drop policy if exists "guardar mis respuestas" on public.attempts;
create policy "guardar mis respuestas" on public.attempts
  for insert with check (auth.uid() = user_id);

-- Lista de espera (antes de abrir las ventas). Solo se escribe desde el servidor.
create table if not exists public.waitlist (
  email text primary key,
  source text,
  created_at timestamptz not null default now()
);

alter table public.waitlist enable row level security;
