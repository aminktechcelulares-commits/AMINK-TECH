-- AMINK TECH · Supabase (proyecto qgnmoeyrbicdwjxnbfwd)
-- Ejecutar una vez en SQL Editor. Esquema real que usan admin.html e index.html:
--   una fila por sección: path = 'store/<seccion>' (privado), 'public/catalog', 'public/logo', 'images/<id>' (públicos)

create table if not exists public.ep_store (
  path       text primary key,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz default now()
);

alter table public.ep_store enable row level security;

grant select on public.ep_store to anon;
grant select, insert, update, delete on public.ep_store to authenticated;

drop policy if exists catalogo_publico_lectura on public.ep_store;
drop policy if exists admin_autenticado on public.ep_store;

-- El catálogo público solo puede leer lo publicado (nunca store/*: clientes, costos, PIN, ventas)
create policy catalogo_publico_lectura on public.ep_store
  for select to anon
  using (path like 'public/%' or path like 'images/%');

-- Solo el/los correos del administrador pueden leer y escribir todo
create policy admin_autenticado on public.ep_store
  for all to authenticated
  using ((auth.jwt() ->> 'email') in ('aminktechcelulares@gmail.com'))
  with check ((auth.jwt() ->> 'email') in ('aminktechcelulares@gmail.com'));
