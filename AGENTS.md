# Gestión Académica 360 — Instrucciones para Agentes

> Este archivo (y su copia exacta `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Si editás uno, copiá el contenido al otro en el mismo cambio. Nunca deben divergir.

**Gestión Académica 360** es una plataforma de gestión académica y trazabilidad multi-tenant que opera como capa de orquestación sobre Moodle: consolida calificaciones, detecta atrasos, gestiona comunicación saliente con aprobación, equipos docentes, encuentros, coloquios, liquidaciones de honorarios y auditoría completa. Cada institución es un tenant aislado. El nombre dice el alcance: una vista **360** de lo académico, docente y administrativo — y todo queda auditado.

**Objetivo vigente:** dejar el producto **listo para usar y mostrar**: sin vulnerabilidades conocidas, con todos los flujos de la demo funcionando y con un frontend moderno y pulido. Todo trabajo se organiza en el **Plan de puesta a punto** (sección más abajo).

---

## Stack Tecnológico (real)

Esta tabla describe lo que **hay** en el repo. Si el código cambia el stack, actualizá esta tabla en el mismo cambio.

### Backend
| Componente | Tecnología | Notas |
|------------|-----------|-------|
| Lenguaje | **Python 3.13** (local) | El Dockerfile todavía usa 3.11 → pendiente alinear |
| Framework | **FastAPI** | API REST async |
| ORM | **SQLAlchemy 2.0** (async, asyncpg) | Queries SOLO en repositories |
| Migraciones | **Alembic** | Una migración por cambio de schema. Nunca `ALTER TABLE` en el startup |
| Base de datos | **PostgreSQL** | Tests sobre SQLite (`tests/conftest.py`) |
| Validación | **Pydantic v2** | DTOs request/response; `extra='forbid'` |
| Auth | **JWT** (access 15 min + refresh rotation) | Secretos desde variables de entorno, nunca en código |
| Passwords | **bcrypt** (hoy) | La KB pide Argon2id → migración pendiente, no bloqueante para la demo |
| Cifrado en reposo | **AES-256-GCM** | PII (DNI, CUIL, CBU) y secretos; clave desde entorno |
| Background jobs | Worker async dentro del proceso de la API | Cola de comunicaciones |
| Integraciones | **Moodle Web Services** | `app/integrations/moodle_ws.py` |
| Testing | **pytest** + pytest-asyncio + httpx | ~720 tests |

### Frontend
| Componente | Tecnología | Notas |
|------------|-----------|-------|
| Framework | **React 19** + **TypeScript** | Sin `any`, sin class components |
| Bundler | **Vite** | HMR en dev |
| Ruteo | **React Router v7** | Guards por rol con `RoleRoute` |
| Estilos | **Tailwind CSS v4** | Tokens en CSS (`@theme`). Sin CSS modules; inline solo para valores dinámicos |
| Animación | **Motion** (`motion/react`) | Respetar `prefers-reduced-motion` |
| Carruseles | **Embla Carousel** (`embla-carousel-react`) | |
| Íconos | **lucide-react** | |
| Gráficos | **Recharts** | |
| HTTP | **Axios** | Cliente único en `src/services/api.ts` con refresh transparente |

### Infraestructura
| Componente | Tecnología |
|------------|-----------|
| Contenedores | Docker + docker-compose (API + Postgres + worker) |
| Deploy | Easypanel |
| Observabilidad | Logs + OpenTelemetry (opcional, extra `otel`) |

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. El detalle técnico vive en `docs/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito y alcance |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Sistema, integraciones, propiedades de seguridad |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Auth, RBAC, matriz de capacidades, impersonación |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, ERD, migraciones |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas codificadas (RN-XX) |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Funcionalidades por épica |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E (importación, mensajería, auth) |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones y estructura |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones cerradas |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | ⚠️ Inconsistencias a resolver ANTES de codear |
| [11_historias_de_usuario.md](knowledge-base/11_historias_de_usuario.md) | Historias + criterios de aceptación |
| [docs/PRD.md](docs/PRD.md) | Requerimientos de producto y RNF |
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Clean Architecture, estructura, seguridad |

> ⚠️ **Roles del dominio**: ALUMNO · TUTOR · PROFESOR · COORDINADOR · NEXO · ADMIN · FINANZAS.

---

## Skills

Cargá la skill del contexto **ANTES** de escribir código y aplicá sus patrones.

| Contexto | Skill | Dónde |
|----------|-------|-------|
| Diseño de UI, tokens, componentes | `tailwind-design-system` | `.agents/skills/` |
| Ayuda contextual en pantallas | `help-system-content` | `.agents/skills/` |
| Cambios planificados | `opsx:propose`, `opsx:apply`, `opsx:archive`, `opsx:explore` | `.claude/skills/` |
| Base de conocimiento | `kb-creator` | `.claude/skills/` |

> `dashboard-crud-page` (en `.agents/skills/`) viene de otro proyecto (asume Zustand y entidades por sucursal). **No aplica** a este repo; no la uses.

---

## Plan de puesta a punto

Tres fases en orden. No se arranca una fase sin cerrar la anterior (salvo tareas marcadas como independientes).

### Fase S — Seguridad ✅ cerrada (2026-11-18, aprobada por el usuario)

Cada ítem se corrigió con **TDD**: test que reproduce el ataque (rojo) → fix mínimo → suite completa (786 tests verdes).

| # | Severidad | Hallazgo | Fix aplicado | Test |
|---|-----------|----------|--------------|------|
| S-01 | Crítica | Secreto JWT hardcodeado | `JWT_SECRET` obligatorio (≥32) en `Settings` | `test_security_config.py`, `test_auth_jwt.py` |
| S-02 | Crítica | Refresh token usable como access | Claim `type`; `verify_token(expected_type=…)` | `test_auth_jwt.py`, `test_auth_security.py` |
| S-03 | Crítica | Auditoría tomaba identidad del header `X-User-ID` | Actor e impersonador desde el JWT; IP y user-agent | `test_middleware/test_audit_middleware.py` |
| S-04 | Crítica | Fugas entre tenants (usuarios, materias, carreras, cohortes, inbox) | Queries con `tenant_id`; ajeno → 404 | `test_cross_tenant_admin.py`, `test_inbox_router.py` |
| S-05 | Crítica | Registro público abierto | `ALLOW_PUBLIC_REGISTER=false` por defecto + `GET /auth/config` | `test_auth_security.py` |
| S-06 | Alta | `/auth/refresh` stub | Rotación con detección de reuso; `/logout` revoca | `test_auth_security.py` |
| S-07 | Alta | 2FA falso | `enrol`/`confirm`/`disable` autenticados; secreto cifrado; login pide TOTP | `test_auth_security.py` |
| S-08 | Alta | Clave PII `"dev-key"` | `ENCRYPTION_KEY` (base64, 32 bytes) + `app/db/rotate_encryption_key.py` | `test_security.py`, `test_rotate_encryption_key.py` |
| S-09 | Alta | Backdoor `user`/`testuser` | Eliminado | `test_auth_security.py` |
| S-10 | Alta | Sin rate limit | 5 fallos / 15 min por IP+email → 429 (`app/core/rate_limit.py`, en memoria) | `test_auth_security.py` |
| S-11 | Alta | Hard deletes | Soft delete en avisos, estructura, roles de usuario y grants | varios |
| S-12 | Alta | Validación floja | `extra='forbid'` en 30+ schemas de request; sin `dict` crudo | `test_cross_tenant_admin.py` |
| S-13 | Crítica | Análisis: PROFESOR/TUTOR sin asignación veía todo ("modo demo") | 403 sin asignación; monitor general solo COORD/ADMIN (F2.7) | `test_analisis.py` |
| S-14 | Alta | Inbox: responder un mensaje ajeno por id | Solo participantes del hilo, mismo tenant | `test_inbox_router.py` |
| S-15 | Crítica | Escalada: COORDINADOR/FINANZAS tenían `usuarios:gestionar` y podían autoasignarse ADMIN | Matriz RBAC = KB §3 con `sync_rbac` (revoca); solo ADMIN otorga ADMIN; nadie cambia sus roles | `test_rbac_seed_sync.py`, `test_cross_tenant_admin.py` |

Infra de tests: `conftest.py` fija `DATABASE_URL` a SQLite antes de importar la app (antes los tests escribían en la base de desarrollo); `aiosqlite` agregado a dev-deps; 19 tests rotos preexistentes corregidos.

**Pendiente (medio/bajo):**
- Tokens en `localStorage` → evaluar cookie httpOnly + CSRF.
- Rate limit en memoria → Redis si hay más de una réplica.
- `run_migration()` en `app/main.py` hace `ALTER TABLE` al arrancar → mover a Alembic.
- Muchos services y routers consultan la DB directo (regla 11) → migrar a repositories al tocarlos.
- FINANZAS tiene `atrasados:ver` y `comunicacion:enviar` (commit `aeaca56`) que la KB no prevé → decisión de producto.
- bcrypt → Argon2id (KB).

### Fase U — Frontend (dominio BAJO salvo auth/guards)

Dirección visual: **"Petróleo + coral"**. Académico y tecnológico a la vez: serif editorial en los títulos, sidebar petróleo oscuro, acento coral y líneas de "traza" animadas como motivo de marca.

- **Paleta:** petróleo `#0E6B72` (primario), teal `#14919B`, coral `#F2704B` (acento), fondo `#F6F8F8`, sidebar `#0B2E33`, texto `#10252A`. Todo definido como tokens OKLCH en `src/index.css` (`@theme` + `.dark`); la serie de gráficos y la paleta de estado están validadas con el script de `dataviz` en ambos temas. El coral solo se usa como texto vía `--color-accent-ink` (contraste). Estados: esmeralda / ámbar / carmesí.
- **Tokens:** definidos una sola vez en `src/index.css` con `@theme` de Tailwind v4. Ningún color hex suelto en componentes.
- **Tipografía:** Inter (UI y texto), **Fraunces** (display: títulos `h1`, saludo del hero, números KPI) y JetBrains Mono (códigos). Números con `tabular-nums`; etiquetas de sección en versalitas con `tracking` amplio (`SectionTitle`, `eyebrow`).
- **Superficies:** tarjetas blancas con borde sutil y sombra suave; hero con gradiente petróleo + aurora coral + grano; sidebar oscuro con brillo y grano; hover con elevación y tilt leve.
- **Efectos (con criterio):** contadores animados en métricas, aparición escalonada de listas, indicador animado en el sidebar, carrusel de avisos/accesos en el Dashboard, fondo de login con gradiente animado. Todo efecto se apaga con `prefers-reduced-motion`.
- **Componentes base** en `src/components/ui/` (Button, Card, Badge, Input, Table, Modal, StatCard, Carousel, EmptyState, Skeleton). Las páginas los consumen; no reinventan estilos.
- **Límites:** componentes < 200 LOC; páginas grandes se parten en subcomponentes en `src/features/<modulo>/`.
- **Accesibilidad:** contraste WCAG AA, foco visible, navegación por teclado en carruseles y modales.
- **Orden de trabajo:** tokens + UI base → AppLayout (sidebar/topbar) → Login → Dashboard → resto de páginas.
- **Gráficos:** antes de escribir uno, cargar la skill `dataviz` y validar la paleta con su script. Paleta de estado del gráfico de avance validada por tema (esmeralda → ámbar → carmesí; el ámbar siempre entre los otros dos); serie única en `--color-chart-1`. Sin donuts: barras, medidores o tiles.

**Estado (2026-11-18):**
- ✅ Tokens light/dark en `src/index.css` + capa de compatibilidad que reestiliza las clases heredadas (`.card`, `.btn`, tablas, modales, tabs) — las 15 páginas ya usan el diseño nuevo.
- ✅ `components/ui/` (Button, Card, Badge, StatCard con tilt y count-up, Carousel Embla accesible, Skeleton, EmptyState, PageHeader, AnimatedNumber).
- ✅ Shell: `SessionContext` (un solo `/me`), `config/navigation.ts` como única fuente de menú y guards, Sidebar con indicador animado, Topbar, drawer mobile.
- ✅ Login con hero animado, carrusel, paso 2FA, registro solo si `/auth/config` lo habilita.
- ✅ Dashboard por rol con datos reales: KPIs, carrusel de avisos, avance académico, comunicaciones, liquidado por período, accesos rápidos.
- ✅ Equipos docentes muestra nombres (backend resuelve docente/rol/contexto).
- ⏳ Migrar páginas heredadas a `components/ui/` y `features/<modulo>/` (hoy funcionan vía la capa de compatibilidad). Prioridad: Usuarios (541 LOC), Tareas, Avisos, Calificaciones.
- ⏳ Liquidaciones abre en el período actual aunque los datos demo sean de ene–abr 2026 → abrir en el último período con datos.

### Fase D — Demo lista

- Todos los roles navegan sin errores de consola ni 4xx/5xx inesperados.
- Seed demo idempotente y con un usuario por rol (incluye FINANZAS y NEXO).
- README con instrucciones de arranque y credenciales demo.

---

## Reglas Duras (no negociables)

Estas reglas son **contrato**. Romperlas es un defecto, no una decisión de estilo. Ante conflicto entre la KB y este archivo, prevalecen las reglas duras.

### Generales
1. **No buildear automático.** Nunca ejecutar `npm run build`, bundle o compilación sin pedido explícito del usuario. Levantar servidores de desarrollo y correr tests sí está permitido.
2. **No commitear sin pedido explícito.** `git add`/`commit`/`push` SOLO cuando el usuario lo pide. Si estás en la rama default, ramificá antes.
3. **Conventional Commits sin `Co-Authored-By`.** Formato `tipo(scope): mensaje`. Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`. Scopes: `auth`, `tenancy`, `users`, `alumnos`, `materias`, `comisiones`, `entregas`, `comunicacion`, `equipos`, `encuentros`, `coloquios`, `liquidaciones`, `auditoria`, `moodle`, `api`, `ui`. JAMÁS agregar atribución a IA ni `Co-Authored-By`.
4. **Tests sin mocks de DB.** Base real o efímera. Mockear la base invalida el test.
5. **Pydantic schemas con `extra='forbid'`** en todo schema de request.
6. **snake_case en Python.**
7. **PascalCase en componentes React.** Nombre del componente y del archivo. Sin `any`, sin class components.

### Seguridad y arquitectura (fallan en code review)
8. **Identidad SIEMPRE desde la sesión** (JWT verificado). JAMÁS desde URL, body, header ni ningún dato de la petición. Esto define usuario, roles y tenant.
9. **Multi-tenancy row-level.** `tenant_id` en cada tabla; todo query filtra por tenant. Un recurso de otro tenant responde **404**, no 403.
10. **RBAC fino `modulo:accion`.** Cada endpoint declara `check_permission(...)`. **Fail-closed**: sin permiso → 403.
11. **Capas:** Routers → Services → Repositories → Models. Sin lógica de negocio en routers; sin queries fuera de repositories.
12. **Secretos y PII cifrados con AES-256.** Ningún secreto en el código ni con valor por defecto.
13. **Soft delete siempre.** Nunca `db.delete()`.
14. **Identidad por UUID interno.** El legajo nunca es credencial.
15. **≤500 LOC por archivo backend**, componentes React < 200 LOC. Una migración Alembic por cambio de schema.
16. **Cobertura**: ≥80% líneas, ≥90% reglas de negocio. **Strict TDD.**
17. **Al cerrar cualquier change**, actualizar `CHANGES.md` (y este archivo si cambió el stack o el plan).

---

## Agent Governance — Autonomía por dominio

| Nivel | Dominios | Comportamiento |
|-------|----------|----------------|
| **CRÍTICO** | auth, multi-tenancy, RBAC, audit log, liquidaciones, core-models, migraciones | Solo análisis y propuesta. Sin aprobación humana explícita, no se escribe código. La Fase S ya está aprobada en su alcance (S-01…S-12); cualquier cosa fuera de esa tabla vuelve a pedir aprobación. |
| **MEDIO** | lógica de dominio, integraciones (Moodle), seeds, pipelines | Implementar con checkpoints; surfacear decisiones no obvias. |
| **BAJO** | UI sin lógica crítica, estilos, catálogos, documentación | Autonomía total si pasan los tests. Reportar en el resumen. |

---

## Flujo de trabajo

```
1. Leer este archivo + la KB relevante + docs/ARQUITECTURA.md
2. Ubicar la tarea en el Plan de puesta a punto (S-NN / Fase U / Fase D) o en CHANGES.md (C-NN)
3. Verificar el nivel de governance            → CRÍTICO = propuesta y aprobación primero
4. Cargar la skill correspondiente
5. TDD: test que falla → fix mínimo → suite completa verde
6. Verificar en la app corriendo (no solo tests) cuando el cambio es visible
7. Actualizar CHANGES.md / este archivo; marcar el ítem como hecho
```

---

## Operación local

```bash
# Backend (desde la raíz; usa .env con DATABASE_URL, JWT_SECRET, ENCRYPTION_KEY)
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --port 8000

# Frontend
cd frontend && npm run dev          # http://localhost:5173

# Seeds (orden): roles/permisos → admin → demo
PYTHONUTF8=1 .venv/Scripts/python -m app.db.seed        # sincroniza la matriz RBAC (idempotente, revoca sobrantes)
.venv/Scripts/python -m app.db.seed_admin
PYTHONUTF8=1 .venv/Scripts/python -m app.db.seed_demo   # Windows necesita UTF-8 (imprime emojis)

# Rotar la clave de cifrado de PII (re-cifra todas las columnas, en una transacción)
OLD_ENCRYPTION_KEY=<base64> .venv/Scripts/python -m app.db.rotate_encryption_key

# Tests (el venv tiene que estar en el PATH: test_migration invoca `alembic`)
PATH="$PWD/.venv/Scripts:$PATH" python -m pytest tests/ -q

# Frontend: chequeo de tipos y lint (no generan artefactos; no es un build)
cd frontend && npx tsc --noEmit -p tsconfig.app.json && npx eslint src
```

**Trampas conocidas**
- `seed_demo` **no es idempotente** hasta que se cierre la Fase D: correrlo dos veces duplica datos.
- La migración `5b6c7d8e9f0a` repunta 15 FKs de la tabla legada `usuarios` a `users`. Si una base nueva falla con FK hacia `usuarios`, falta `alembic upgrade head`.
- `.env` contiene credenciales: no se lee ni se imprime. Nuevas variables se documentan en `.env.example`.

**Credenciales demo** (solo entorno local): `admin@activia-trace.com` / `admin123`; docentes y alumnos del seed demo con `demo123`.
