# Projects Context

Memoria técnica del portafolio. Recoge lo que **realmente** contiene cada
proyecto, verificado leyendo su código, no lo que se recuerda de él.

Norma de esta base de conocimiento:

- **Todo lo que se afirma aquí sale del código, de la documentación interna del
  proyecto o del historial de git.** Cuando algo es un recuerdo sin respaldo en
  el código, va marcado como `[SIN VERIFICAR]`.
- Cuando el código contradice el recuerdo, se registran **las dos versiones** y
  se marca el conflicto. No se elige por cuenta propia lo que va al portafolio.
- **Ningún secreto entra aquí**: ni tokens, ni contraseñas, ni claves de API, ni
  IDs de calendario o de chat. Se nombra el servicio, nunca la credencial.
- Los proyectos fuente viven fuera de esta carpeta y son **solo lectura**.

Última actualización: **20 de agosto de 2026**.

---

## Índice

Orden de publicación acordado: **cuatro casos destacados** en filas a sangre y
**cuatro secundarios** en lista. Con ocho proyectos, ocho filas a pantalla
completa convertían la portada en un scroll sin final y le quitaban peso justo a
los dos que deben dominar.

| # | Proyecto | Carpeta fuente | En el portafolio |
|---|---|---|---|
| 01 | [AG Identity](#1-ag-identity) | `AG-IDENTIFY` | **Destacado** · `views/proyecto-ag-identity.html` |
| 02 | [ArgosMonitors](#2-argosmonitors-argosrisk) | `ArgosRisk` | **Destacado** · `views/proyecto-argosmonitors.html` |
| 03 | [SITI Colombia](#3-siti-colombia) | `siticolombiaProyecto` | **Destacado** · `views/proyecto-siticolombia.html` |
| 04 | [AgroIA](#6-agroia) | `agroiaproyecto` | **Destacado** · `views/proyecto-agroia.html` |
| 05 | [Southern Roofing & Remodeling](#5-southern-roofing--remodeling) | `southerntxroofing` | Secundario · `views/proyecto-southern-roofing.html` |
| 06 | [Recordatorios por WhatsApp](#4-recordatorios-automáticos-por-whatsapp) | `automatizacionWAProyecto` | Secundario · `views/proyecto-whatsapp.html` |
| 07 | [B&B Turismo y Negocios](#7-bb-turismo-y-negocios-bbpfto) | `BBPFTOProyecto` | Secundario · `views/proyecto-byb.html` |
| 08 | [GoodMovies](#8-goodmovies) | `goodmoviesproyecto` | Secundario · `views/proyecto-goodmovies.html` |

Las secciones de este documento conservan el orden en que se investigaron, que
**no** es el de publicación. La numeración de arriba es la que manda.

Conflictos abiertos y preguntas pendientes: [§ Verificaciones pendientes](#verificaciones-pendientes).

---

# 1. AG Identity

- **Carpeta fuente**: `C:\xampp\htdocs\AG-IDENTIFY`
- **Sitio**: https://gestiondeportivaag.com/
- **Repositorio**: `https://github.com/jorge0630/AG-IDENTIFY` (privado)
- **Periodo verificado en git**: 30 jul 2026 – 15 ago 2026 (**44 commits** en `main`)
- **Autoría**: proyecto de **dos personas trabajando presencialmente, codo a codo**.
  El reparto de commits (`jorge0630` 31 · `Camilo` 13) **no refleja el reparto real
  del trabajo**: se dividían por ramas, no por áreas. Ver [Mi participación](#mi-participación).

## Contexto

Identificación de jugadores por **huella dactilar** para torneos deportivos. Un
administrador enrola jugadores y huellas desde un panel web; en las canchas, una
aplicación de escritorio identifica al jugador **sin conexión** y muestra su
ficha: foto, nombre, documento, edad, posición, equipo, categoría, camiseta y
estado de inscripción.

**Regla de oro del sistema**: la app de cancha **solo identifica, nunca enrola**.
El matching 1:N corre en el dispositivo, jamás en el servidor.

## Problema

En un torneo con cientos de jugadores, verificar que quien salta a la cancha es
quien está inscrito se hace con papel y buena fe. El fraude de identidad —jugar
con la ficha de otro, o en una categoría de edad que no corresponde— no tiene
forma práctica de detectarse en el momento.

Dos restricciones marcan el diseño:

1. **En una cancha no hay internet fiable.** El sistema tiene que decidir sin red.
2. **Quien opera no es técnico.** El resultado debe ser "es este jugador" o "no
   está registrado", sin lecturas intermedias que interpretar.

## Solución — arquitectura de cuatro piezas

```
Admin (panel Filament)
  → Agente de Captura (Windows, bandeja, 127.0.0.1:9877)
    → Lector Futronic FS88 (P/Invoke a FTRAPI 4.2)
      → Laravel / MySQL  (base maestra, fuente de verdad única)
        → Sync incremental HTTP (Sanctum)
          → SQLite cifrado (SQLCipher) en el equipo de cancha
            → Identificación 1:N offline
```

Monorepo a propósito: **un cambio de contrato toca los tres componentes a la vez**.

| Carpeta | Qué es | Stack | Estado |
|---|---|---|---|
| `Backend/` | Panel admin + API + base maestra + **sitio público de AG** | Laravel 12 · PHP 8.2 · MySQL · Filament 5 · Sanctum · Pest · Vite + Tailwind 4 | Funcionando. **38 archivos de prueba, ~384 casos** |
| `Agente/` | App de bandeja de Windows que presta el lector USB al navegador | .NET 10 · `WinExe` + WinForms · Kestrel · P/Invoke FTRAPI · x64 | Funcionando con lector real |
| `Mobile/` | App de escritorio que identifica offline en cancha | .NET 10 · MAUI/WinUI · MVVM (CommunityToolkit) · sqlite-net-sqlcipher | Compila y arranca; registro verificado; **identificación con lector real aún sin probar** |
| `Shared/` | `Core` (contratos sin plataforma, `net10.0`) + `Biometria.Windows` (todo el P/Invoke) | .NET 10 | Integrado y validado |
| `Spike/` | Prueba de concepto desechable del interop Futronic | .NET 10 | Cerrado, ya cumplió |

> **`Mobile/` no es una app móvil.** El nombre es herencia de cuando el destino
> era Android. Hoy compila para Windows (`net10.0-windows10.0.19041.0`).
> Android está **diferido, no descartado**: `Platforms/Android` se conserva y
> `Core` no tiene dependencias de plataforma, así que se reactiva agregando su
> TFM al `.csproj`.

## Tecnologías verificadas

**Backend** — `composer.json` / `package.json`:
Laravel 12 · PHP 8.2+ · Filament 5.7 · Laravel Sanctum 4 · Laravel Tinker ·
Pest 3 · Laravel Pint · Vite 7 · Tailwind CSS 4 · MySQL/MariaDB.

**Escritorio y agente** — `.csproj`:
.NET 10 · .NET MAUI (WinUI) · C# · CommunityToolkit.Mvvm 8.4 ·
sqlite-net-sqlcipher 1.9 · SQLitePCLRaw bundle_e_sqlcipher ·
Microsoft.Extensions.Http / Logging / Options · P/Invoke con `AllowUnsafeBlocks`.

**Hardware y biometría**:
Futronic **FS88** (`VID_1491 / PID_0088`) · Futronic Standard SDK 4.2
(`FTRAPI.dll`, `ftrScanAPI.dll`) · formato de plantilla `FUTRONIC-PROP-4.2`.

> **Corrección respecto al recuerdo inicial**: la base de datos es **MySQL /
> MariaDB**, no PostgreSQL. Verificado en `Backend/.env` (`DB_CONNECTION=mysql`,
> `DB_DATABASE=ag_identify`) y en la documentación interna del proyecto.

## Modelo de datos

Dominio en español. **9 tablas del contrato base (v2.2)**:
`jugadores`, `huellas`, `equipos`, `categorias`, `torneos`, `torneo_categorias`,
`inscripciones`, `dispositivos`, `actividad`.

**+5 tablas de control de acceso** (posteriores al contrato, no bajan a la
tablet): `roles`, `permisos`, `permiso_rol`, `rol_usuario`,
`asignaciones_usuario`.

**+7 tablas del módulo de sitio web**: `configuracion_sitio`, `anuncios`,
`publicaciones`, `galeria_imagenes`, `solicitudes_inscripcion`, `partidos`, y la
ampliación de `torneos` con campeón y subcampeón.

**+11 tablas de la fase de competición (v2.5, agosto 2026)**: `formatos_juego`,
`fases`, `sesiones_registro`, `partido_equipos`, `partido_jugadores`,
`sustituciones`, `partido_eventos`, `sanciones`, `sancion_cumplimientos`,
`sincronizacion_cuarentena`, más la migración de `partidos` a fases.

Enums del dominio (`app/Enums/`): `Dedo`, `TipoDocumento`, `EstadoInscripcion`,
`EstadoAcceso`, `EstadoPublicacion`, `EstadoSolicitud`, `EstadoPartido`,
`EstadoSancion`, `EstadoSesionRegistro`, `MetodoVerificacion`,
`OrigenSancion`, `RolPartidoJugador`, `TipoEventoPartido`.

Decisiones del modelo que vale la pena contar:

- `jugadores 1:N huellas` con **`UNIQUE(jugador_id, dedo)`**.
- **Un jugador no tiene equipo directo.** El equipo sale de `inscripciones`: la
  pregunta correcta no es "¿de qué equipo es?" sino "¿con qué equipo está
  inscrito **en este torneo**?".
- `inscripciones` apunta a **`torneo_categoria_id`**, una sola clave foránea.
  Eso hace **imposible por diseño** inscribir a alguien en una categoría que el
  torneo no abrió.
- **Soft deletes** en todo lo principal; `actividad` es un log **inmutable**
  (solo `created_at`).
- Índices de sincronización (`updated_at`, `deleted_at`) en toda tabla que baja
  al equipo de cancha.
- **Elegibilidad por edad = edad al 31 de diciembre** del año de
  `torneos.fecha_inicio`. Vive en un solo sitio: `Categoria::esElegible()`.

## API REST `/api/v1`

Verificada en `Backend/routes/api.php`. Bearer Sanctum; `401` significa
revocación; todas las respuestas llevan `server_time`.

| Endpoint | Para qué |
|---|---|
| `POST /dispositivos/registrar` | Provisión del equipo. Público, con `throttle:10,1` |
| `GET /ping` | Comprobación de conectividad desde el equipo de cancha |
| `GET /sync` | Sincronización incremental |
| `POST /actividad` | Eventos de identificación. **Descarta cualquier `template` que llegue** |
| `POST /actas/eventos` | **Canal transaccional del acta**: sube los eventos del partido registrados offline |
| `GET /jugadores/{id}/foto` | Foto optimizada, autenticada |
| `GET /equipos/{equipo}/logo` | Escudo del club |

Las rutas autenticadas pasan por `auth:sanctum` **más** un middleware propio,
`EnsureDispositivoActivo`.

## Problemas resueltos — el material fuerte del caso

### 1. El umbral por defecto del lector aceptaba a la persona equivocada

El SDK trae **FARN 166** como valor por defecto. Durante el spike, con ese
umbral, **un dedo no enrolado fue aceptado como el jugador enrolado** (alcanzó
FARN 268).

Datos de la misma sesión de medición:

| Caso | FARN alcanzado |
|---|---|
| Genuino, misma posición que el enrolamiento | 1000 |
| Genuino, posición natural | 885 |
| **Impostor (otro dedo de la misma persona)** | **268** |

El motor discriminaba bien —885 frente a 268 es una separación amplia—; el
problema era solo el umbral. Con 166 y mil jugadores, el riesgo acumulado es de
**~4,8% por identificación: una de cada veinte aceptaría a la persona
equivocada**.

**Decisión: FARN 345**, que lleva el riesgo a ~1 entre 270.000. Configurable en
`OpcionesBiometria.UmbralFarn`.

### 2. `FTRIdentifyN` no dice "es este"

Devuelve **todos** los candidatos por encima del umbral. Si dos jugadores
distintos quedan a menos de **100 puntos** entre sí, quedarse con el más alto
sería adivinar. Se resuelve como `IdentificacionAmbigua` y se pide repetir la
huella.

Varias plantillas del **mismo** jugador coincidiendo no es ambigüedad: se
registra como posible enrolamiento duplicado, que además es una detección útil.

### 3. La escala de calidad estaba mal calibrada por culpa del simulador

El umbral original era 60 sobre 100 — un valor heredado del **capturador
simulado**, no del hardware. `FTRAPI` entrega calidad en **escala 1–10**, así
que ese umbral rechazaba capturas excelentes. Corregido a **6 sobre 10**
(`HUELLA_CALIDAD_MINIMA`).

### 4. Optimizar el matcher no servía para nada

Medido contra el FS88:

| Dato | Valor medido |
|---|---|
| Tamaño de plantilla | **2001 bytes** (el buffer que exige el SDK es 3333) |
| Comparación 1:N contra 1000 plantillas | **279 ms (~3.600 plantillas/s)** |
| Captura del dedo para identificar | **~2,7 s** |
| Duración del enrolamiento (5 muestras) | ~14 s |
| Calidad típica, dedos normales | 8–10 |
| Calidad, huella desgastada | 5 |

**La comparación es el 0,07% del tiempo total.** El cuello de botella es el
sensor, no el algoritmo. Consecuencia de diseño: el esfuerzo se fue al flujo de
captura, no al matcher.

Ese mismo dato invalidó un argumento del contrato: **3.600 plantillas/s frente a
las ~100/s que el fabricante declara para su SDK ANSI/ISO — 36 veces más
rápido**. Particionar la búsqueda por equipo dejó de ser necesario por
rendimiento; se mantuvo por precisión, que es otra razón.

### 5. El navegador no puede hablar con un lector USB

De ahí el **Agente de Captura**: una aplicación de bandeja que expone el lector
como HTTP local. **Es el navegador quien lo llama, nunca el servidor de Laravel.**

Contrato HTTP:

| Endpoint | Qué hace |
|---|---|
| `GET /estado` | El panel lo consulta antes de habilitar el botón, para decir "no se detecta el agente" en vez de fallar con un error de red. Devuelve `listo`, que es el booleano que decide |
| `POST /capturar` | Activa el lector y pide el dedo cinco veces (~14 s). Devuelve plantilla en base64, calidad y formato |
| `GET /progreso` | Guía en vivo para el operador. El panel lo sondea cada 400 ms |

`GET /progreso` existe porque `POST /capturar` **no responde hasta terminar**:
sin él, la pantalla quedaba muda los ~14 s que dura el enrolamiento. Traduce las
señales del SDK (`SIGNAL_TOUCH_SENSOR`, `SIGNAL_TAKE_OFF`, `SIGNAL_FAKE_SOURCE`)
a instrucciones en español. Se eligió **sondeo** antes que SSE o WebSocket por
ser lo más simple que funciona: es información accesoria y perder una lectura no
rompe nada.

Los motivos de error (`lector_no_disponible`, `tiempo_agotado`,
`captura_fallida`, `calidad_insuficiente`, `dedo_falso`, `ocupado`) son **parte
del contrato** y se traducen desde la enum interna en `MotivosApi.Desde()`, para
no acoplar el JSON al nombre de un símbolo de C#.

### 6. El bug que habría llenado la base de huellas falsas, en silencio

`WebApplication.CreateBuilder` busca `appsettings.json` en el **directorio de
trabajo**, no en el del binario. Lanzado desde un acceso directo, el menú Inicio
o una tarea programada, el agente **no encontraba su configuración** y caía a los
valores por defecto — donde `ModoSimulado` es `true`.

Es decir: **el agente arrancaba en modo simulado y el panel habría guardado
plantillas falsas sin un solo mensaje de error.**

Resuelto fijando `ContentRootPath = AppContext.BaseDirectory`. Sin ese arreglo el
arranque automático no era seguro.

Defensas que se añadieron alrededor del mismo riesgo:

- **Aviso modal al arrancar en modo simulado.** Un clic de molestia a cambio de
  que nadie enrole plantillas falsas por descuido.
- **Laravel rechaza enrolar con formato `SIMULADO` en producción.**

### 7. Sincronización que no puede perder registros

Protocolo anti-pérdida, en seis pasos:

1. El equipo de cancha **sube primero** sus eventos encolados.
2. Pide `GET /sync?desde = ultima_sync − 5 min` — un **solape deliberado** que
   evita huecos por desfase temporal.
3. Aplica **upserts idempotentes** por id, en orden: catálogos → jugadores → huellas.
4. Aplica bajas **con cascada local**: al borrar un padre borra los hijos, porque
   el `updated_at` de los hijos no cambia y el servidor no los reporta.
5. **Solo si todo se guardó bien** persiste `server_time` como nueva
   `ultima_sync`. **Nunca usa su reloj local.**
6. Lee el bloque `dispositivo` (detecta reasignación de torneo) y descarga las
   fotos **al final**, para que la identificación nunca espere por una imagen.

### 8. Las imágenes dejaban de verse al cambiar de host

Las rutas se construían con `APP_URL`. Bastaba entrar por la IP de la red local
en vez de por `localhost` para que el panel dejara de mostrar imágenes ya
guardadas: los campos se quedaban girando en "Esperando tamaño", **sin ningún
error**. Se cambió a rutas relativas en `config/filesystems.php`, y ahora el
mismo código funciona en `localhost`, en `127.0.0.1:8000`, en la IP de red y en
el dominio con HTTPS.

## La fase de competición: del enrolamiento al acta del partido (agosto 2026)

Es la evolución más reciente y la que convierte el sistema de "identificador de
jugadores" en **software de competición**. Implementada: 11 tablas nuevas, 7
enums, 4 recursos de Filament (`Fases`, `Partidos`, `Sanciones`, `Cuarentena`) y
un endpoint de API propio.

**El flujo real en cancha**: el administrador elige fase → partido → equipo; la
app abre una **sesión de registro** y va acreditando titulares por huella contra
el cupo del formato de juego. Cada huella pasa seis validaciones en orden:

1. Identificar al jugador.
2. Su inscripción pertenece al equipo seleccionado, en el torneo-categoría del partido.
3. La inscripción está activa y sin fecha de retiro.
4. No tiene sanciones vigentes en ese torneo-categoría.
5. No fue registrado ya en este partido.
6. No se superó el cupo de titulares.

### El matching se hace contra la plantilla, no contra el torneo

**~20–30 huellas del equipo seleccionado, no los miles del torneo.** Dos razones:
es dramáticamente más rápido y **reduce el riesgo de falso positivo**, que escala
con el tamaño del conjunto — y ya se había observado uno real durante el spike.

La contrapartida: si el jugador no está en ese conjunto, la app no puede decir a
qué equipo pertenece. La solución es una **búsqueda en dos pasos**: sin
coincidencia en la plantilla, se reintenta contra el torneo completo **solo para
producir un mensaje de error útil, nunca para aceptar el registro**.

Eso permite diez mensajes distintos donde un sistema corriente diría "no
autorizado". Los tres que mejor lo ilustran:

- *"El jugador pertenece a {equipo}. Seleccione dicho equipo para verificarlo."*
  → es del rival de **este** partido: es un error de operación, no un fraude.
- *"No habilitado. Pertenece a {equipo}. No puede participar en este encuentro."*
  → es de otro equipo del torneo: eso sí es el fraude que el sistema existe para
  detectar.
- *"Jugador suspendido. {motivo}. Le restan {n} fecha(s)."*

### La ruta de excepción, y por qué no es una puerta trasera

Con ~1000 jugadores hay que contar con **20–50 casos de biometría no viable**
—dedos gastados, cicatrices, lesiones—. Sin ruta de excepción, **un titular cuya
huella no lee bloquea el partido**, y eso no sobrevive al primer domingo.

El administrador busca al jugador, la app muestra **foto y documento**, confirma
visualmente y registra con `metodo_verificacion = manual` y **motivo
obligatorio**.

Lo que impide que se convierta en el camino cómodo:

- **Tope configurable** de verificaciones manuales por equipo y partido, con
  alerta al superarlo.
- **El acta nunca oculta la excepción, la documenta.** Distingue siempre
  "certificado por huella" de "aceptado manualmente", y el panel reporta el
  **porcentaje de excepciones por partido y por equipo**.

> Esa distinción es exactamente lo que le da credibilidad al sistema. Un acta que
> no dijera cómo se acreditó cada jugador valdría lo mismo que la hoja de papel
> que vino a reemplazar.

### La realidad de la cancha, escrita en el modelo

| Situación real | Cómo se resolvió |
|---|---|
| Se inicia con 9 o 10 y se completa después | Confirmar por debajo del cupo **exige motivo** y marca el acta como `alineacion_incompleta`. Los que llegan tarde quedan marcados con `incorporacion_tardia` |
| Error de captura después de confirmar | Se puede **anular** una fila con motivo obligatorio mientras el acta no esté cerrada. No se borra: soft delete + registro en `actividad`. *Corregir un error no puede requerir tocar la base a mano* |
| El acta hay que congelarla | Acción explícita **Cerrar acta** → nada admite modificación: ni alineación, ni sustituciones, ni resultado. Reabrir exige motivo y queda en el log |
| Los expulsados | Se eligen **entre quienes participaron**, no en un campo de texto libre |
| El cierre del acta dispara las sanciones | Mientras el acta esté abierta, la expulsión aún puede corregirse |

### El conflicto entre dos máquinas — la decisión más fina del proyecto

Caso real contemplado: el administrador no sincronizó y **volvió a empezar el
registro desde cero en otra máquina**. La regla es *prevalece la sesión más
reciente*, con tres condiciones que la hacen segura:

1. **"El último" se mide por cuándo se registró, no por cuándo llegó al
   servidor.** El contraejemplo que obligó a esta condición: la máquina A se
   descarga el domingo con 8 jugadores en su cola; el administrador sigue en la B
   y sincroniza esa tarde; el martes se enciende A y sincroniza. **Los datos de A
   llegan después pero son los viejos.** Con "gana el último que llega", A
   pisaría a B — exactamente al revés de lo buscado.
2. **La unidad de conflicto es la sesión, no la fila.** Gana **completa** la de
   `iniciada_en` más reciente, para no mezclar 8 filas de una con 3 de otra y
   producir un acta incoherente.
3. **La sesión perdedora se archiva, no se borra**, con alerta en el panel:
   *"se reemplazó el registro del dispositivo A (8 jugadores, 15:02) por el del
   dispositivo B (11 jugadores, 15:40) — ver / restaurar"*.

### Cuarentena: nada se descarta en silencio

El log de `actividad` no servía como canal de subida —es inmutable y descarta
plantillas—, así que se construyó uno transaccional. Los eventos **rechazados**
(partido ya cerrado, sesión reemplazada, validación fallida) caen en
`sincronizacion_cuarentena` con su carga en JSON y el motivo, **se conservan y se
le muestran al administrador**.

Dos límites de la cola del cliente que hubo que levantar para que eso funcionara:
la confirmación pasó de **por lote a por evento** (un rechazo detenía el lote
entero) y el evento dejó de **borrarse al subirlo** (un evento rechazado no tenía
dónde vivir).

## Decisiones técnicas destacables

| Decisión | Razón |
|---|---|
| Formato propietario `FUTRONIC-PROP-4.2`, no ANSI-378 | El SDK gratuito no genera ANSI-378. El de pago cuesta 1000 USD **y compara 36× más lento** (~100/s vs ~3.600/s) |
| Guardar la imagen cruda como registro maestro | Es la garantía de portabilidad frente a un formato propietario. **Pendiente**, y es el pendiente número uno |
| 10 dedos enrolables, no 2 | La calidad varía mucho entre dedos: se capturan varios y se conservan los mejores. `huellas.dedo` pasó a VARCHAR; `App\Enums\Dedo` es la fuente de verdad |
| x64, no x86 | El SDK 4.2 trae `Bin\x64`; se verificó empíricamente en el spike |
| SQLite **cifrado** (SQLCipher) en el equipo de cancha | Es dato biométrico, viaja fuera del servidor |
| El agente escucha **solo en `127.0.0.1`** | Uno accesible desde la red dejaría a cualquier equipo pedirle capturas al lector. Además, no obliga a abrir puertos en el firewall |
| CORS restringido por origen | Es la defensa real del agente, no el puerto |
| Mutex global: una sola instancia | Dos agentes pelearían por el puerto y por el lector, que es un recurso físico exclusivo |
| Un token Sanctum por dispositivo, en Secure Storage | No hay columna `token` en la base |
| Código de registro de un solo uso: 8 caracteres, 24 h | Desactivar el dispositivo **revoca sus tokens** → recibe 401, borra todo y vuelve a la pantalla de registro |
| Autorización por **tres ejes independientes**: rol + alcance de equipo + vigencia | Un "usuario temporal" es la combinación de los tres, no un rol aparte. El equipo de una inscripción **lo resuelve el servidor** contra el alcance, nunca el formulario |
| Sin empaquetado MSIX en la app de escritorio | Se despliega como ejecutable en los PC de cancha: más simple de instalar y actualizar |
| Disco público para el sitio, privado para las fotos de jugador | Las fotos son de **menores** y solo salen por endpoint autenticado. Los escudos y flyers son material de promoción y deben verse sin sesión |

## El sitio público

La raíz del backend **es el sitio público de AG**, no una redirección al panel:
quien llega a la dirección del proyecto es un club o un padre buscando el torneo,
no un administrador.

Todo su contenido sale de la base, no de las plantillas — se administra desde el
grupo **Sitio web** del panel: contenido web (empresa, portada, contacto, redes,
SEO, torneos destacados), anuncios y flyers, publicaciones, galería y la bandeja
de **solicitudes** donde caen los clubes que se inscriben desde la web.

Los seeders del sitio son **idempotentes**: se pueden volver a correr sin
duplicar nada ni pisar lo que se haya cambiado desde el panel.

## Estado actual

> ⚠️ **Cómo se declara el estado en el portafolio.** El sistema **no** se
> presenta como «En producción» a secas. El backend, el sitio público y el
> agente sí lo están; la app de cancha está construida y su registro
> verificado, pero **su identificación contra el lector real sigue sin probar**
> — y ésa es justo la afirmación titular del proyecto. La ficha dice
> «En producción · app de cancha en validación», y la página de caso lo explica
> en un párrafo propio. No suavizar eso: es la parte por la que preguntará
> cualquier entrevistador técnico.

| Componente | Estado |
|---|---|
| Backend | Funcionando. **38 archivos de prueba, ~384 casos** |
| Módulo de competición (partidos, actas, sanciones) | Implementado: 11 tablas, 4 recursos de panel, endpoint de acta |
| Sitio público | Funcionando y administrable, con partidos en vivo del torneo destacado |
| Agente de Captura | Funcionando con lector real (calidad 9–10 verificada) |
| App de escritorio | Compila y arranca; registro y sustituciones en cancha. **Identificación con lector real aún sin probar** |
| Android | Diferido, no descartado |

> **Ojo con el README del proyecto**: sigue diciendo "178 pruebas pasando", una
> cifra anterior a la fase de competición. El conteo real sobre el árbol actual
> es de ~384 casos en 38 archivos. Usar la cifra medida, no la del README.

Pendientes principales, en el orden en que están priorizados en el repositorio:

1. **Guardar la imagen cruda** al enrolar.
2. **Log a archivo** en el agente y en la app — hoy no dejan rastro, y en una
   cancha no hay depurador que conectar.
3. Ejercitar la identificación de la app contra el lector real.

> La *ruta de excepción* figuraba como pendiente transversal #3 hasta julio;
> **ya está implementada** dentro de la fase de competición (`MetodoVerificacion::Manual`
> con motivo obligatorio y tope configurable).

## Mi participación

**Desarrollo conjunto de dos personas, trabajando presencialmente durante todo el
proyecto.** Ambos tocaron backend y frontend; el reparto fue **por ramas de
trabajo, no por áreas de conocimiento**: cada uno escribía las líneas de su rama,
pero los dos conocen el código completo, qué hace y qué no, y las tecnologías y
librerías que usa.

**El historial de git no refleja ese reparto** y no debe usarse para deducirlo.
Como referencia interna, los archivos que Camilo tocó en `main` se concentran en
`Backend/` (361), `Mobile/` (49), `Documentacion/`, `capturas/`, `recursos-marca/`
y `Agente/`. En la rama del sitio público (`feature/landing`) firma 8 de 17
commits, y la rama de diseño del panel (`feature/diseno`) es suya.

**Fórmula acordada para el portafolio**: *"Desarrollo conjunto, en pareja"* — sin
apropiarse del proyecto entero ni minimizar la participación.

## Evidencia visual disponible

**Capturadas el 20 de agosto de 2026** levantando el backend en local
(`php artisan serve` + MySQL de XAMPP) y ya incorporadas al portafolio:

| Archivo en `src/img/` | Qué muestra |
|---|---|
| `ag1.jpg` | Escritorio del panel: 8 equipos, 206 jugadores, **89,8% de huellas enroladas (185 de 206)**, 1 torneo en curso |
| `ag2.jpg` | Listado de huellas con dedo, **formato `FUTRONIC-PROP-4.2`** y **calidad en escala 1–10**. Es la prueba visual de las decisiones biométricas |
| `ag3.jpg` | Gestión de competición: torneos con estado, categorías, equipos e inscritos |
| `ag4.jpg` | Programación de partidos por fase, con columna de acreditación por huella |
| `ag5.jpg` | Dispositivos de cancha: UUID, torneo asignado, código de registro **«Consumido»** y última sincronización |
| `ag6.jpg` | Registro de actividad: «Jugador identificado por huella» y «Sin coincidencia», con el equipo que lo generó |
| `ag7.jpg` | Sitio público, administrado entero desde el panel |
| `ag8.jpg` | Listado de jugadores con posición, número de huellas y estado |

> `ag2`, `ag5` y `ag6` son las tres más valiosas: enseñan en pantalla lo que el
> resto del caso solo puede afirmar por escrito — el formato de plantilla, el
> flujo de provisión de un dispositivo y la identificación funcionando.

Datos del entorno capturado (base local con datos de prueba, nombres generados):
206 jugadores, 1.382 huellas, 10 equipos, 4 torneos, 12 partidos.

También existen en la carpeta fuente, sin usar todavía:
`capturas/app-escritorio/` (3 capturas de la app de cancha: reposo, ficha del
jugador y sincronización), `capturas/prototipo_landingpage.png` y
`recursos-marca/*.png` — estos últimos son renders de marca, **no capturas
reales**.

**Sigue faltando** una captura de la pantalla de enrolamiento con el agente
activo: exige el lector FS88 conectado.

## Por qué merece el primer lugar del portafolio

Es el único proyecto que cruza **cuatro capas de tecnología distintas** —panel
web, API, aplicación de escritorio y hardware USB— y el único donde las
decisiones están respaldadas por **mediciones propias contra el hardware**, no
por lo que dice la documentación del fabricante.

Tiene además las tres mejores historias técnicas del portafolio, y ninguna es
"usé tal framework":

1. **El falso positivo con FARN 166**: una medición propia que contradijo el
   valor por defecto del fabricante y cambió una decisión de diseño.
2. **El agente que arrancaba simulado en silencio**: un bug de configuración que
   habría llenado la base de huellas falsas sin un solo mensaje de error.
3. **El conflicto entre dos máquinas**: la regla "gana el último" era incorrecta
   hasta que se midió por *cuándo se registró* en vez de *cuándo llegó*.

Las tres tienen la misma forma: **lo obvio estaba mal, y se descubrió pensando en
qué pasa un domingo en una cancha.**

---

# 2. ArgosMonitors (ArgosRisk)

- **Carpeta fuente**: `C:\xampp\htdocs\ArgosRisk`
- **Demo**: https://demo.argosmonitors.com/
- **Repositorio**: `https://github.com/jorge0630/ArgosRisk` (privado)
- **Periodo verificado en git**: 25 may 2026 – 23 jul 2026 (32 commits)
- **Autoría en git**: `jorge0630` 41 commits (dos identidades) · `Camilo` 7 commits

> La carpeta se llama `ArgosRisk` y el producto se presenta como
> **ArgosMonitors**. Es el mismo proyecto: el nombre del repositorio quedó del
> arranque. En el portafolio se usa **ArgosMonitors**.

> 🔒 **Decisión tomada: no se nombra al fabricante del producto ni al cliente de
> la demo en el portafolio.** Los nombres reales están en la documentación del
> proyecto fuente y **no se copian aquí**. En los textos públicos se dice
> "un producto SaaS de cumplimiento para empresas colombianas" y "una empresa del
> sector". Tampoco se publica ningún NIT.

## Contexto

Producto **SaaS de cumplimiento**: gestión de riesgo y control interno para
empresas colombianas. El entorno de demo trabaja sobre datos de una empresa real
del sector.

El dominio concreto es **SARLAFT** — el sistema colombiano de administración del
riesgo de lavado de activos y financiación del terrorismo — más gestión de
empleados bajo el Código Sustantivo del Trabajo.

**Multi-tenant por `empresa_id`** en cada tabla. Existe además un módulo de
parametrización global cuyos catálogos **no llevan `empresa_id`**: niveles y
factores de riesgo SARLAFT, criterios de debida diligencia y tipos de documento
de contrapartes. Se siembran una sola vez para todo el sistema.

## Problema

Una empresa obligada a cumplir SARLAFT tiene que demostrar, ante una auditoría,
que evaluó el riesgo de cada contraparte antes de vincularla, que revisó a sus
representantes, accionistas y beneficiarios finales contra listas restrictivas,
que documentó la decisión y que hace seguimiento periódico.

Sin sistema, eso vive en carpetas de Excel y correos. **La evidencia no es
reconstruible** y, en una auditoría, no poder demostrar el control equivale a no
haberlo hecho.

## Solución — nueve módulos

Verificado en `app/Modules/` y `routes/web.php`.

| Módulo | Qué resuelve |
|---|---|
| **Vinculación** | El flujo completo de alta de una contraparte: creación → revisión → asignación de analista → aprobación o rechazo, con observaciones y recálculo de score |
| **Contrapartes** | Maestro de terceros (persona natural / jurídica), con panel de **vencimientos** y exportación |
| **Evaluaciones** | Debida diligencia (DD), **debida diligencia intensificada (DDI)** y seguimiento periódico, con criterios, respuestas y evidencias adjuntas |
| **Denuncias** | Canal ético: formulario **público y anónimo** + bandeja interna con asignación, estados, notas y evidencias |
| **Empleados** | Expediente laboral completo: documentos versionados, capacitaciones, dotaciones, disciplinarios, evaluaciones y control de turnos |
| **Gestión Documental** | Documentos con versiones y flujo de aprobación: envío a revisión → aprobar / rechazar → descarga y previsualización |
| **Reportes** | Expediente en PDF, matriz de riesgo en Excel, próximas evaluaciones |
| **Parametrización** | Catálogos globales y **motor de reglas de riesgo** editable desde la interfaz |
| **Usuarios** | Alta, activación y reseteo de contraseña. Restringido a `admin` y `super_admin` |

### Lo que sostiene el módulo de Vinculación

Acciones verificadas en `app/Modules/Vinculacion/Actions/`:

`CrearVinculacionAction` · `CrearVinculacionExternaAction` · `IniciarRevisionAction` ·
`CalcularPuntajeSarlaftAction` · `EvaluarReglasRiesgoAction` ·
`RecalcularPuntajeFormalAction` · `AprobarVinculacionAction` · `RechazarVinculacionAction`

Modelos: `Vinculacion`, `RepresentanteLegal`, `Accionista`, `BeneficiarioFinal`,
`ScreeningLista`, `VinculacionDocumento`, `VinculacionObservacion`.

Tres detalles que muestran que el dominio se entendió de verdad:

- **Beneficiario final** como entidad propia, no como un campo. Es exactamente lo
  que exige la norma y lo primero que se pasa por alto.
- **Marca PEP** (persona expuesta políticamente) conmutable de forma
  independiente sobre representante legal, accionista y persona natural — tres
  rutas distintas, porque son tres roles distintos.
- **`scoring_snapshots`**: el puntaje se congela en el tiempo. Cuando alguien
  pregunte en dos años por qué se aprobó esta contraparte, la respuesta está
  guardada con la puntuación que tenía **ese día**, no con la de hoy.

### Tres portales públicos sin autenticación

Una decisión de producto que además es de arquitectura: los tres flujos que
tienen que funcionar para gente de fuera no pasan por login.

| Ruta | Para quién |
|---|---|
| `/canal-denuncias` | Denuncia anónima + consulta de estado con radicado |
| `/portal-empleados` | El empleado registra su turno con la cédula y consulta su historial |
| `/formulario-vinculacion` | El proveedor se registra y actualiza sus documentos por su cuenta |

En el portal de empleados, la regla escrita en la documentación del proyecto es
explícita: **nunca exponer datos sensibles** — solo nombre, cargo, área, sede y
sus propios turnos.

## Legislación colombiana implementada en el código

No es un CRUD con nombres en español: la lógica de negocio **es la norma**.

| Concepto | Norma | Dónde vive |
|---|---|---|
| Jornada ordinaria máxima | Art. 160 CST | `horas_ordinarias_diarias` en `EmpConfigHoraria` |
| Recargo nocturno (19h–6h) | Art. 168 CST | `hora_inicio_nocturna` / `hora_fin_nocturna` |
| 8 tipos de hora (ordinaria, extra diurna/nocturna, dominical, festivo) | Art. 168–172 CST | `ClasificadorHorasService` — 8 buckets contables |
| Descanso no remunerado dentro de la jornada | Art. 167 CST | `minutos_descanso`, se descuenta **antes** de clasificar |
| Pago por períodos, máximo mensual | Art. 134 CST | `EmpConfigPeriodoNomina` — quincenal / mensual / personalizado |
| Festivos colombianos | Ley 51/1983 | `EmpFestivo`, sembrables por año |

**El flujo completo del turno**: el empleado entra su cédula en el portal público
→ el sistema **detecta automáticamente el tipo de turno** por hora y día de la
semana → `ClasificadorHorasService::clasificarYGuardar()` reparte las horas en
los 8 buckets según el CST → el administrador aprueba o rechaza.

Todo eso es **parametrizable sin tocar código**: la página
`/empleados-configuracion` tiene 8 pestañas, cada una con su propia ruta PATCH.

## Tecnologías verificadas

**Backend** — `composer.json`:
Laravel 12 · PHP 8.2+ · **Inertia.js 2** · `spatie/laravel-permission` 6 (roles
y permisos) · `spatie/laravel-activitylog` 4 (auditoría) ·
`barryvdh/laravel-dompdf` 3 (expedientes PDF) · `rap2hpoutre/fast-excel` 5
(matriz de riesgo) · `tightenco/ziggy` 2 (rutas en el frontend) ·
`symfony/intl` · Pest.

**Frontend** — `package.json`:
**React 19** · TypeScript 5.7 · Inertia React 2 · **Tailwind CSS 4** ·
Vite 6 · Headless UI 2 · **Framer Motion 12** · lucide-react ·
clsx + tailwind-merge · ESLint 9 + Prettier (con `organize-imports` y
`prettier-plugin-tailwindcss`) · fuentes Inter, Inter Tight y Syne.

**Infraestructura**: Docker + docker-compose + nginx (`docker/`), GitHub Actions
(`.github/workflows`). **57 migraciones.** La migración a PostgreSQL está
declarada como prioridad de mediano plazo, no ejecutada.

## Mi participación — el rediseño

Es la parte mejor documentada y la más atribuible.

`CLAUDE.md` §9 es un **sistema de diseño completo** escrito para el proyecto, con
una advertencia al frente: *"todo colaborador que toque el frontend DEBE leerla
antes de escribir una sola clase CSS"*.

La dirección declarada: **enterprise premium** con referencia explícita a Linear,
Stripe, Vercel y Apple. Compacto y minimalista, **oscuro por defecto** con light
mode completo, **glassmorphism sutil y solo en dark mode**, profundidad por
sombras en vez de color saturado, y una regla que aparece dos veces: *ningún
elemento clicable se camufla con el fondo*.

El rediseño **"Liquid Glass"** (julio 2026) migró el panel autenticado entero:
shell `PanelLayout` + `panel.css`, **8 módulos con CSS scoped por módulo**, y
retirada del layout anterior. La carpeta `rediseño/assets/css/` contiene el
sistema: `tokens.css`, `tokens-dark.css`, `tokens-light.css`, `theme.css`,
`typography.css`, `elevation.css`, `glass.css` más una hoja por módulo.

Los últimos tres commits del repositorio son de Camilo y dicen exactamente eso:
*"Rediseño de ArgosMonitors 100% 22/07"*, *"rediseño completado"*.

**Reparto del trabajo — confirmado**: igual que en AG Identity, fue **desarrollo
conjunto de dos personas trabajando presencialmente**. Ambos tocaron backend y
frontend, dividiéndose por ramas de trabajo; los dos conocen el código completo,
el dominio y las librerías. **El conteo de commits no refleja el reparto real.**

Lo que sí es individualmente atribuible y demostrable en el árbol: **el sistema
de diseño y el rediseño completo del panel**, documentado por escrito en
`CLAUDE.md` §9 y con la carpeta `rediseño/` como prueba material.

## Estado actual

Demo funcional en https://demo.argosmonitors.com/. **No es un producto terminado
y no debe presentarse como tal**: es la versión que se enseña a un socio
estratégico. En la documentación del proyecto, el módulo de Empleados estaba
marcado como el que iba a presentarse.

Pendientes declarados: migración a Docker + PostgreSQL, vistas de autenticación
menores (forgot / reset / verify / confirm-password) y el super admin.

## Evidencia visual disponible

**Capturadas el 20 de agosto de 2026** levantando el proyecto en local
(`php artisan serve` + `npm run dev`, porque el proyecto estaba en modo Vite dev
y sin el servidor de assets la página sale en blanco):

| Archivo en `src/img/` | Qué muestra |
|---|---|
| `argos1.jpg` | Resumen de cumplimiento: 34 contrapartes activas, flujo de vinculaciones y reparto de riesgo (18 bajo / 12 medio / 2 alto / 2 crítico) |
| `argos2.jpg` | **Expediente de una contraparte**: línea de tiempo del proceso, tarjetas de DD / DDI / seguimiento y el **puntaje SARLAFT con su aguja**, marcado como «Requiere DDI» |
| `argos3.jpg` | Parámetros de clasificación horaria **citando los artículos 160–171 y el 167 del CST** en la propia interfaz |
| `argos4.jpg` | Los **8 conceptos contables** en los que se reparten las horas, con su código |
| `argos5.jpg` | Bandeja del canal de denuncias, distinguiendo casos **anónimos de identificados** |
| `argos6.jpg` | Formulario público de vinculación en **7 pasos**, con *Beneficiarios* como paso propio |
| `argos7.jpg` | Listado de vinculaciones con estado, tipo y nivel de riesgo calculado |
| `argos8.jpg` | Centro de personal: expediente laboral, turnos y documentos por vencer |

> `argos2` y `argos3` son las dos que sostienen el caso entero. La primera
> enseña el puntaje SARLAFT funcionando; la segunda muestra los artículos del
> Código Sustantivo del Trabajo escritos en la interfaz, que es la prueba
> literal de que la norma es la lógica de negocio.
>
> `argos6` confirma en pantalla lo que se había leído en el código: los
> **beneficiarios finales son un paso propio del flujo**, no un campo escondido.

**Anonimización**: el nombre del cliente de la demo aparecía en la barra lateral
y en varios listados. Se sustituyó **en el DOM antes de capturar** —un cambio
temporal en pantalla, sin tocar el proyecto ni su base de datos— por
«Empresa Demo S.A.S.». **Ninguna captura publicada contiene el nombre real ni
su NIT.** Si se vuelven a tomar capturas, hay que repetir la sustitución.

Queda sin usar `Argosmonitor.png` en la raíz de la carpeta fuente. La carpeta
`capturas/` de ese proyecto sigue vacía.

## Qué contar en el portafolio

El ángulo no es "plataforma de gestión de riesgos". Es **software donde la norma
es la lógica de negocio**: ocho tipos de hora que salen del Código Sustantivo del
Trabajo, beneficiarios finales que existen porque SARLAFT los exige, y snapshots
de puntaje que existen porque una auditoría pregunta por el pasado, no por el
presente. Más el rediseño completo del panel, que es trabajo directamente
atribuible y visualmente demostrable.

---

# 3. SITI Colombia

- **Carpeta fuente**: `C:\xampp\htdocs\siticolombiaProyecto`
- **Sitio**: https://siticolombia.co/
- **Repositorio**: `https://github.com/cp327/siticolombiaProyecto`
- **Periodo**: 2025
- **En el portafolio**: publicado como proyecto **01 / 05**

## Contexto

Sistema interno de gestión y programación de tareas para el **sector hotelero**.
Un administrador asigna trabajos por hotel; el técnico ve solo lo suyo y reporta
avance, observaciones y evidencias fotográficas desde su propio panel.

Camilo trabajó en SITI Colombia entre enero y septiembre de 2025 como gestión de
redes y auxiliar de sistemas — el sistema se construyó desde dentro de la
empresa que lo usa.

## Problema

Los técnicos recibían las tareas por teléfono y el seguimiento se perdía por el
camino. Nadie podía decir con certeza qué se había hecho en cada hotel, cuándo,
ni con qué resultado.

## Arquitectura

PHP plano organizado por rol, sin framework. La separación es por carpetas:

```
src/
├── admin/        → vistas, controladores y JS del administrador
├── employee/     → vistas, controladores y JS del técnico
├── config/
│   ├── auth/     → check_session.php, check_role.php
│   └── db/       → conexion.php (MySQLi), logout.php
├── controllers/  → validate_login.php
├── services/     → logTelegram.php
└── public/       → assets y librerías de terceros
```

**Control de acceso por dos guardas incluidas en cada vista**:
`check_session.php` (¿hay sesión?) y `check_role.php` (¿el rol correcto?). Es la
versión sin framework de un middleware.

## Modelo de datos

Base `siticolombia` en MySQL, conexión **MySQLi con `mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT)`**
— excepciones en vez de errores silenciosos — y charset `utf8mb4`.

Cinco tablas, deducidas de las consultas del código:

| Tabla | Para qué |
|---|---|
| `usuarios` | Administradores y técnicos, con rol y estado |
| `hoteles` | Los clientes |
| `tareas` | El trabajo asignado |
| `tarea_participante` | Qué técnicos van en cada tarea — relación N:M |
| `tarea_observaciones` | Reportes de avance del técnico, con imágenes |

`tarea_participante` es la decisión de modelo que importa: **una tarea puede
tener varios técnicos**, no uno.

## Tecnologías verificadas

PHP · MySQL (MySQLi) · JavaScript · **SB Admin 2** (plantilla de panel sobre
**Bootstrap 4**) · jQuery · **DataTables** (con integración Bootstrap 4) ·
**Chart.js** · Font Awesome · **API de Telegram**.

> El recuerdo inicial mencionaba **Select2**; no aparece en la carpeta de
> librerías del proyecto. Sí están DataTables, Chart.js y Font Awesome, que no
> se habían mencionado.

## El bot de Telegram — la decisión más interesante

`src/services/logTelegram.php` envía a un chat de Telegram cada movimiento del
sistema: alta de administrador, alta de empleado, alta y actualización de hotel,
alta y actualización de tarea, cambio de estado de tarea y de observación.

Detalles del servicio:

- Fecha y hora en **`America/Bogota`**, con los meses traducidos a español a
  mano — el formateador nativo devolvía nombres en inglés.
- Los mensajes salen en **Markdown**, así que el registro se lee formateado en el
  propio chat.
- El envío es un `file_get_contents` contra la API de Telegram: la vía más
  directa posible.

**Por qué es la decisión buena**: resolvió la trazabilidad con una fracción del
esfuerzo que habría costado construir un panel de auditoría propio, y además
puso el registro donde el administrador ya mira — su teléfono — en vez de en una
pantalla a la que habría que entrar.

> En el código del repositorio, el token del bot y el id del chat están **en
> blanco**. No hay credenciales expuestas.

## Estado actual

En producción en siticolombia.co.

## Evidencia visual

Ya en el portafolio: `siti1.png` … `siti6.png` (6 capturas). **No hacen falta
capturas nuevas.**

## Qué representa en la evolución

La etapa **anterior al framework**: PHP plano, plantilla de panel comprada,
autenticación resuelta a mano. Y aun así, con dos decisiones que se sostienen —
la relación N:M de participantes y el bot como registro de auditoría. Es el
contrapunto que hace visible el salto hasta AG Identity.

---

# 4. Recordatorios automáticos por WhatsApp

- **Carpeta fuente**: `C:\xampp\htdocs\automatizacionWAProyecto`
- **Repositorio**: `https://github.com/cp327/automatizacionWAProyecto`
- **Periodo**: 2025
- **En el portafolio**: publicado como proyecto **03 / 05**

> ✅ **Conflicto resuelto (20 ago 2026).** El recuerdo hablaba de facturas y
> vencimientos; el código lee un calendario. **Decisión: el portafolio documenta
> solo la integración Calendar → WhatsApp**, que es lo que el código respalda.
> No se escribe nada sobre facturas, vencimientos ni períodos.

## Lo que hay en el repositorio

**Un solo archivo**: `script.js`, 78 líneas, un **Google Apps Script**.

Función `enviarRecordatoriosHoyWhatsApp()`:

1. Fija la ventana del día: `hoy` a las 00:00 y `mañana` a las 00:00.
2. `CalendarApp.getCalendarById(...).getEvents(hoy, maniana)` — lee los eventos
   de **hoy** de un calendario de Google compartido.
3. **Si no hay eventos, sale sin enviar nada** y lo anota en el log.
4. Formatea la fecha en español (`es-ES`, día / mes en letra / año).
5. Numera los títulos de los eventos y **normaliza los espacios**
   (`.trim().replace(/\s+/g, ' ')`) — los títulos escritos a mano en el
   calendario venían con espacios dobles y saltos.
6. **Rellena la lista hasta 4 con `"N/A"`.** Es el detalle técnico del proyecto:
   las plantillas de WhatsApp Business exigen **exactamente** el número de
   parámetros declarado. Con menos, la API rechaza el mensaje.
7. Envía la plantilla `recordatorio_eventos` (idioma `es_CO`) a cada contacto de
   la lista, vía `POST` a **Graph API v22.0** de Meta, con `UrlFetchApp` y
   `Authorization: Bearer`.
8. `muteHttpExceptions: true` + `Logger.log(response)` — el fallo de un contacto
   **no corta el envío a los demás**, y la respuesta queda registrada.

**Componentes de la plantilla**: un `header` con el nombre del destinatario y un
`body` con la fecha más los cuatro eventos.

## Tecnologías verificadas

Google Apps Script · Google Calendar API (`CalendarApp`) · `UrlFetchApp` ·
**WhatsApp Cloud API** de Meta (Graph API v22.0) · plantillas de mensaje
aprobadas de WhatsApp Business.

**No hay** base de datos, backend, ni panel. Toda la programación la aporta el
disparador de tiempo de Apps Script.

## Lo que el código NO contiene — no escribir esto en el portafolio

El recuerdo inicial describía un sistema para una empresa de **servicios
contables**, con **facturas**, **fechas de vencimiento** y períodos de
notificación **mensual / quincenal / semanal**, más un aviso el día antes del
cierre.

**Nada de eso está en el código.** No hay lógica de facturas, ni de vencimientos,
ni de períodos: hay un calendario y los eventos de hoy. Se buscó en toda la
carpeta `htdocs` código de facturas o vencimientos y **no existe**.

Queda anotado aquí para que ninguna sesión futura lo reintroduzca por error.

> El único material relacionado con contabilidad en `htdocs` es
> `contadores/index.html`, una landing de "Contadores Cartagena" hecha con
> Tailwind CDN — **otra cosa, no este proyecto**.

Las credenciales del script (token de Meta, `phoneNumberId`, id de calendario y
números de teléfono) están **enmascaradas con asteriscos** en el repositorio. No
hay secretos expuestos.

## Estado actual

En producción, según la ficha del portafolio.

## Evidencia visual

Ya en el portafolio: `WA1.png` (el mensaje recibido en el teléfono). **No hacen
falta capturas nuevas.** La captura es buena porque muestra el resultado, que es
lo único visible de una automatización sin interfaz.

## Qué representa en la evolución

Automatización pura: **sin interfaz, sin base de datos y sin servidor**. El valor
está en haber elegido las tres piezas que ya existían —calendario, Apps Script y
la API de WhatsApp— en vez de construir un sistema. Y en los detalles que solo
aparecen al integrar de verdad: el relleno hasta cuatro parámetros, la
normalización de títulos y el aislamiento de fallos por contacto.

---

# 5. Southern Roofing & Remodeling

- **Carpeta fuente**: `C:\xampp\htdocs\southerntxroofing`
- **Sitio**: https://southerntxroofing.com/
- **Repositorio**: **no existe** — la carpeta no está bajo git.
  **Decisión: la ficha va sin botón "Ver el código"**, solo "Visitar el sitio"
- **Periodo verificado por fechas de archivo**: 16 jun 2026 – 26 jun 2026
- **En el portafolio**: **falta**

## Contexto

Cliente real en **Estados Unidos**: una empresa de techado y remodelación en
Texas. El encargo, según el brief del propio proyecto, **no era cambiar colores y
tipografías**, sino modernizar la experiencia, mejorar la percepción de
profesionalismo y **aumentar conversiones**.

## Problema

El sitio corría sobre WordPress con tema Astra y bloques Gutenberg + Spectra.
Funcionaba, pero se veía exactamente como lo que era: una plantilla de WordPress.
Sin arquitectura orientada a conversión y sin jerarquía visual.

Restricción del encargo: **mantener las URL actuales** por SEO, conservar la
configuración de All In One SEO, los formularios de WPForms y el botón de
WhatsApp.

## La decisión que define el proyecto

**No se reemplazó WordPress.** El sitio sigue corriendo con WP + Astra con
normalidad. Lo que se hizo fue **inyectar encima** mediante el plugin **WPCode**,
en cuatro snippets:

| Snippet | Contenido |
|---|---|
| HTML | Estructura de la landing (`<div class="sr-page">` con todas las secciones) |
| CSS | `SR - Estilos Landing.css` — 47 KB, tokens, componentes y responsive |
| JS | `SR - Landing JS.js` — 64 KB, inyección y comportamiento |
| Fonts | Google Fonts en el `<head>`, **antes** de que el CSS las necesite |

Ventajas de esa vía frente a un child theme: **menor riesgo, mantenimiento más
simple, el cliente sigue pudiendo editar contenido, y desarrollo más rápido.**

Cómo se resolvió convivir con el tema sin romperlo:

- **Todas las clases llevan prefijo `sr-`** (Southern Roofing), con patrón BEM
  (`.sr-bloque__elemento--modificador`). Cero colisiones con Astra o Spectra.
- El CSS **oculta el chrome de WordPress** solo en las páginas intervenidas,
  seleccionando por `body.home` y por `page-id` concretos. El resto del sitio
  queda intacto.
- El JS **sale por la puerta en la primera línea** si el `body` no es una de esas
  páginas: `if (!isHome && !isAbout && !isColors && !isGallery) return;`.
- Los comentarios nativos de WordPress, que quedaban ocultos dentro de
  `.site-main`, **se reubican** dentro de la sección de testimonios en vez de
  perderse.

## Qué se construyó

Cuatro páginas completas, no una landing:

| Página | Contenido |
|---|---|
| **Home** | Hero con Ken Burns, servicios, About, galería, Why Us, testimonios, contacto |
| **About** | Sección propia |
| **Colors Roofing** | Catálogo de colores con tarjetas ampliables en el visor |
| **Gallery** | **168 fotos reales en 9 categorías**, con filtros y "cargar más" |

Comportamientos implementados en el JS:

- **Visor de imágenes (lightbox)** con flechas, navegación por teclado, **gesto
  de deslizar en móvil** y contador.
- **`IntersectionObserver`** para las animaciones de scroll, con
  `obs.unobserve()` — la animación ocurre **una sola vez** — y **fallback**: si
  el navegador no lo soporta, todo se marca visible en lugar de quedar invisible.
- **Menú hamburguesa** que se cierra al pulsar cualquier enlace.
- **Hoja inferior en móvil para las tarjetas de servicio**: la descripción larga
  no cabe en la tarjeta, así que vive en un panel que se abre al tocarla.
- **Filtros por categoría + paginación** en la galería completa.
- **Botón de volver arriba**, posicionado sobre el WhatsApp flotante.

### El formulario va a WhatsApp, no a un servidor

El formulario de contacto **intercepta el submit**, arma un mensaje con los cinco
campos y abre `wa.me` con el texto ya escrito.

La razón, escrita en el propio handoff: es el canal de conversión preferido del
cliente **y evita depender de un servidor de correo** — que en WordPress
compartido es la fuente número uno de leads perdidos en silencio.

## Sistema de diseño

Tokens en CSS, definidos en el propio archivo:

- **Navy profundo** (`#0c2340`) como color principal: transmite confianza y
  contrasta con el dorado.
- **Dorado** (`#c8a843`) como **acento único**, reservado a CTAs y eyebrows —
  para que no se sature.
- Tipografías **Rubik** (títulos) e **Inter** (cuerpo).
- Escalas de sombra (`--sh`, `--sh-md`) y de radio (`--r`, `--r-lg`).

Decisiones documentadas: hover de tarjetas con `translateY(-6px)` —feedback sin
exageración—, tarjetas de Why Us que **invierten colores** al pasar el ratón, y
**Ken Burns en el hero** para dar vida al fondo **sin usar vídeo**, compatible
con todos los navegadores.

## Método de trabajo

Está documentado en `DESIGN_HANDOFF.md` y es parte del caso: el cliente envía una
captura → se audita la sección contra un marco de criterios escrito de antemano →
se documenta la decisión → se implementa → se anota en el log de cambios.

El log recoge secciones **eliminadas** por redundantes (la barra de estadísticas,
duplicada del hero; el banner de CTA, ya cubierto por el hero, el WhatsApp
flotante y el formulario). Quitar es parte del trabajo.

## Tecnologías verificadas

WordPress · tema Astra · Gutenberg + Spectra · **plugin WPCode** (inyección de
snippets) · CSS3 con custom properties · JavaScript ES5/ES6 sin dependencias ·
`IntersectionObserver` · Google Fonts (Rubik, Inter) · All In One SEO ·
WPForms · MonsterInsights · Really Simple Security.

**Sin frameworks de frontend, sin build, sin dependencias externas.** Todo el
comportamiento es JavaScript plano dentro de una IIFE.

## Estado actual

En producción. Home, About, Colors y Gallery implementadas. **Contact quedaba
pendiente** de auditoría según el log de cambios.

## Evidencia visual disponible

**Capturadas el 20 de agosto de 2026** del sitio en producción, ya en el
portafolio:

| Archivo en `src/img/` | Qué muestra |
|---|---|
| `str1.jpg` | Portada: titular de servicios, sello de acreditación y los dos botones de contacto |
| `str2.jpg` | Tarjetas de servicios, las que en móvil abren una hoja inferior con la descripción |
| `str3.jpg` | Presentación de la empresa con sus especialidades y años de experiencia |
| `str4.jpg` | Galería de trabajos reales en rejilla, con filtros y carga progresiva |

Se tomaron del sitio en vivo y no de los `fullpage_snapshot_*.png` de la carpeta
fuente, que pesan entre 2 y 13 MB cada uno.

En la carpeta fuente quedan sin usar los `vista-*-old.html`, que conservan el
estado **anterior** de cada página.

> Eso permite montar un **antes y después real**, que sería la pieza más
> convincente de este proyecto y algo que ningún otro del portafolio puede
> ofrecer. Está pendiente: exige capturar los `-old.html` en local y decidir
> cómo enfrentarlos visualmente.

## Qué representa en la evolución

Cliente extranjero, encargo comercial, y una decisión de ingeniería que no es la
obvia: **trabajar con las restricciones del sistema del cliente en vez de contra
ellas**. Es el proyecto que demuestra criterio de producto, no solo de código.

---

# 6. AgroIA

- **Carpeta fuente**: `C:\xampp\htdocs\agroiaproyecto`
- **Repositorio**: `https://github.com/cp327/agroiaproyecto`
- **Periodo**: 2025
- **En el portafolio**: publicado como proyecto **02 / 05**

## Contexto

Proyecto del **Técnico en inteligencia artificial** de la Universidad Tecnológica
de Bolívar (2025). Recomendación de cultivos por **municipio y año** para el
departamento de **Bolívar**, expuesta como un chat.

La premisa de producto: **un agricultor no consulta un modelo estadístico, pero
sí escribe en un chat.**

## Problema

Existen datos públicos de rendimiento agrícola por municipio y cultivo —las
Evaluaciones Agropecuarias Municipales (EVA)— pero están en un CSV de miles de
filas. La información existe y no llega a quien la necesita.

## Solución — tres capas

```
Texto libre del usuario
  → spaCy (es_core_news_sm) + EntityRuler  → extrae MUNICIPIO
  → regex \b(20\d{2})\b                     → extrae AÑO
    → RandomForest (modelo_rendimiento_rf.pkl)
      → predice rendimiento de CADA cultivo del catálogo
        → top 5 por rendimiento predicho
```

### La capa de lenguaje

`app.py` construye patrones para el `EntityRuler` de spaCy a partir de los
municipios reales del dataset, y además **añade patrones para las palabras
sueltas** de los nombres compuestos, saltándose las partículas (`DE`, `LA`, `EL`,
`DEL`) y descartando fragmentos de tres letras o menos.

Motivo: nadie escribe "SAN JUAN NEPOMUCENO" completo. Con el patrón partido, un
"nepomuceno" suelto también resuelve.

Encima hay una **normalización propia** (`normalize_text`) que pasa a mayúsculas
y **elimina tildes** vía `unicodedata.normalize('NFD')` descartando las marcas de
combinación. Sin eso, "Turbaco" y "TURBACÓ" eran municipios distintos.

### La capa de predicción

`recomendar_cultivos()` no predice "qué sembrar" directamente. Hace algo más
honesto: **construye una fila sintética por cada cultivo del catálogo** —con las
medianas de área sembrada y cosechada de ese cultivo, y el rendimiento promedio
histórico de ese municipio— **predice el rendimiento de todas** y devuelve las
cinco mejores.

Cuando no hay histórico de ese cultivo en ese municipio, cae a la mediana global
en vez de fallar.

Variables del modelo:
- Categóricas: `Municipio`, `Cultivo`.
- Numéricas: `Area_Sembrada`, `Area_Cosechada`, `Año`, `Rend_prom_mun_cult`,
  `ratio_cosecha_siembra`.

En el notebook se compararon **LinearRegression, RandomForest y XGBoost**, con
`Pipeline` (`OneHotEncoder` + `StandardScaler`), `train_test_split`,
`GridSearchCV` y métricas `r2_score`, `MAE` y `RMSE`. **El modelo que se desplegó
es el Random Forest.**

### La capa conversacional

Además de la predicción, hay un mapa de **small talk** de unas 20 entradas
agrupadas por intención: saludos, despedidas, feedback, identidad, capacidades,
fuente de datos, confiabilidad, ayuda y casuales.

Lo interesante no son los saludos, son **los límites declarados**. El bot dice
explícitamente que **no** tiene datos de clima, **no** maneja precios ni mercados
y **no** da consejo agronómico (fertilizantes, plagas, riego, suelo) —
remitiendo a un ingeniero agrónomo. Y sobre su propia fiabilidad: *"son
predicciones y deben usarse como guía de apoyo"*.

Un asistente que enumera lo que no sabe hacer es una decisión de diseño, no una
carencia.

### Contexto de conversación

La respuesta devuelve `contexto_actual` con municipio y año, y el frontend lo
reenvía en la siguiente petición. Así funciona el seguimiento: si el usuario
pregunta *"¿y para el año siguiente?"*, el municipio se hereda del contexto. El
backend incluso propone la pregunta de seguimiento en `sugerencias`.

## Tecnologías verificadas

Python 3.12 · **Flask** + flask-cors · **pandas** · **scikit-learn** (vía
`joblib` sobre el pipeline serializado) · **spaCy** con `es_core_news_sm` y
`EntityRuler` · `unicodedata` · `re` · Jupyter Notebook · HTML/CSS/JS plano
en `templates/` y `static/`.

**Datos**: `Evaluaciones-Agropecuarias-Municipales-EVA.csv` y
`Evaluacion-Agricola-Departamento-de-Bolivar.csv` (fuente pública), procesados a
`bolivar_agro_limpio.csv`.

Endpoints: `/` · `/chat` · `/conocerMas` · `/login` · `POST /recomendar` ·
`GET /municipios`.

## Advertencias honestas sobre el estado

Dos cosas que conviene saber antes de presentarlo:

1. **El modelo entrenado y el CSV limpio no están en el repositorio.**
   `modelo_rendimiento_rf.pkl` y `bolivar_agro_limpio.csv` no existen en
   `backend/backend/`. Quien clone el repositorio verá `app.py` arrancar con
   `❌ Error al cargar modelos o datos` y todos los endpoints degradados. El
   notebook sí está, así que el modelo se puede reentrenar.

2. **El login no es autenticación.** `login.script.js` compara contra un objeto
   `registeredUsers` **escrito en el JavaScript del cliente**, y guarda el estado
   en el navegador. Es una puerta de demo, no un control de acceso — y como el
   proyecto es académico y las credenciales son de prueba, es una decisión
   defendible. Lo que no se puede es llamarlo autenticación.

> La ficha actual del portafolio dice *"En línea, con credenciales de prueba"*.
> Es coherente con lo anterior, siempre que exista un despliegue con los
> artefactos que faltan en el repositorio.
> `[SIN VERIFICAR]` — falta confirmar dónde está desplegado.

## Participación

`[SIN VERIFICAR]` — proyecto académico, probablemente en equipo. La carpeta
contiene entregables de grupo (`AgroIA.pptx`, `AgroIA.docx`,
`AgroIA presentacion.pdf`, `Docuemento AgroIA .pdf`) y el mapa de small talk
menciona *"un proyecto de inteligencia artificial"* en plural. Falta confirmar
qué hizo Camilo y qué el resto del equipo.

## Evidencia visual

Ya en el portafolio: `agroia1.png` … `agroia4.png`. **No hacen falta capturas
nuevas.**

## Qué representa en la evolución

El único proyecto de **machine learning** del portafolio, y el único que hace
**procesamiento de lenguaje natural**. Además, la mejor demostración de criterio
de producto en el conjunto: el trabajo difícil no fue entrenar el modelo, fue
decidir que se consultara escribiendo.

---

# 7. B&B Turismo y Negocios (BBPFTO)

- **Carpeta fuente**: `C:\xampp\htdocs\BBPFTOProyecto`
- **Repositorio**: `https://github.com/cp327/BBPFTOProyecto`
- **Periodo verificado por los datos de la base**: julio 2025
- **En el portafolio**: publicado como proyecto **04 / 05**

> **Sobre el nombre y las carpetas duplicadas**: en `htdocs` existen `BBPFTO` y
> `BBPFTOProyecto`, con **contenido idéntico** (26 archivos, mismos nombres y
> tamaños) y **repositorios distintos** (`cp327/BBPFTO` y `cp327/BBPFTOProyecto`).
> El portafolio ya apunta a `BBPFTOProyecto`; se mantiene ese como oficial.
> La base de datos se llama `bybpro`, de donde sale la lectura **B&B** = *B y B*.

## Contexto

Sitio web para una **consultora del sector hotelero y turístico** en Cartagena,
con panel de administración propio. Los logotipos que aparecen en el sitio
—Accor, Decameron, Hilton, InterContinental— se usan como credibilidad por
cadenas atendidas.

## Problema

Una consultora que hacía varias cosas distintas y no lograba explicarlas en una
sola página. El trabajo fue tanto de **estructura de contenido** como de
desarrollo.

## Arquitectura

PHP plano, sin framework. 26 archivos.

```
index.php                        (719 líneas — el sitio público completo)
admin.php                        (354 líneas — login + panel)
config.php                       (lee credenciales desde .env)
assets/
├── controllers/
│   ├── enviar_correo.php        (formulario de contacto)
│   ├── guardar_feed.php         (CRUD del feed, 158 líneas)
│   ├── mostrar_feed.php
│   └── bybpro.sql
├── public/css/  style.css (2160 líneas) · admin.css (336)
├── public/js/   script.js (182) · admin.js (96)
└── public/img/  incluye chains/ con los logos de cadenas
uploads/feed/                    (imágenes subidas desde el panel)
```

## Secciones del sitio

Hero con estadísticas · franja de valores · **servicios** · quiénes somos con
valores en acordeón · cadenas internacionales · socios · **resultados** (cuatro
casos) · **feed de Instagram** · contacto.

## Decisiones técnicas verificadas

### Mobile-first por revelado progresivo

No es "responsive" en el sentido de que todo se apila. El contenido **se
prioriza**:

- Las estadísticas del hero llevan una clase `.stat-mobile-priority`: **en móvil
  solo se muestran las dos primeras**.
- Los servicios se dividen en **prioritarios** (siempre visibles) y
  **secundarios** (ocultos en móvil tras un botón "Ver más servicios").
- De los cuatro casos de resultados, **dos se ocultan en móvil**.
- La imagen de "quiénes somos" **no se carga en móvil**, para ahorrar scroll.
- Los valores pasan de pills a acordeón según el tamaño.

Es una decisión de contenido tomada en el CSS: en una pantalla pequeña, **menos
secciones completas** en vez de las mismas secciones más estrechas.

### Seguridad — más cuidada de lo que la ficha actual sugiere

| Medida | Dónde |
|---|---|
| Contraseña del admin con **`password_verify()`** (hash bcrypt) | `admin.php` |
| **`session_regenerate_id(true)`** tras el login — previene fijación de sesión | `admin.php` |
| Credenciales **fuera del código**, en `.env` leído con `parse_ini_file` | `config.php` |
| Los controladores del panel **verifican la sesión antes de nada** y redirigen con `?error=no_autorizado` | `guardar_feed.php` |
| Consultas con **sentencias preparadas** (`prepare` + `bind_param`) | `guardar_feed.php` |
| Subida validada **por extensión y por MIME real** | `guardar_feed.php` |
| Al eliminar una entrada del feed, **también se borra el archivo del disco** | `guardar_feed.php` |
| Formulario de contacto: `strip_tags`, `FILTER_VALIDATE_EMAIL`, longitudes limitadas (100 / 2000) y **eliminación de saltos de línea para prevenir inyección de cabeceras** | `enviar_correo.php` |
| El endpoint de correo **solo acepta POST** | `enviar_correo.php` |

La prevención de header injection en el formulario de correo es un detalle que
casi nadie implementa en un sitio de este tamaño.

### Otros

- **Banner de cookies** con aceptación persistida.
- Animaciones con **AOS** (Animate On Scroll).
- Feed de Instagram **administrable**: se sube la imagen desde el panel, se
  guarda en `uploads/feed/` y se muestra en el sitio. Evita depender de la API de
  Instagram, que exige revisión de app y token que caduca.

## Modelo de datos

Base `bybpro` en MySQL/MariaDB, `utf8mb4_spanish_ci`. Dos tablas, pero **solo
una está viva**:

- **`feed_instagram`** — entradas del feed con su imagen. Es lo único que
  gestiona el panel: en `admin.php` la palabra «feed» aparece 12 veces.
- **`testimonios`** — nombre, cargo, empresa, mensaje, calificación (con `CHECK`
  de 1 a 5) y fecha. ⚠️ **Tabla muerta.** La palabra `testimonio` **no aparece
  en ningún `.php` del proyecto**: ni en `admin.php`, ni en `index.php`, ni en
  los controladores. Existe en el volcado SQL y nada más. Es residuo de una
  versión anterior.

> **No escribir que el panel gestiona testimonios.** Ya pasó una vez: la ficha
> de la portada llegó a decir «el cliente administra su feed y sus testimonios»
> y era falso. El panel administra el feed, punto.

El volcado SQL conserva datos de prueba de julio de 2025 con nombres de empresas
de zona franca. **Antes de publicar el repositorio conviene limpiar ese volcado**;
no son secretos, pero son datos de terceros y ruido en una demostración.

## Tecnologías verificadas

PHP 8.2 · MySQL / MariaDB (MySQLi con sentencias preparadas) · JavaScript plano ·
CSS3 · **AOS** · Google Fonts.

## Estado actual

En producción, según la ficha del portafolio.

## Evidencia visual

Ya en el portafolio: `byb1.png` (una sola captura). **No hacen falta capturas
nuevas** por indicación de Camilo, aunque la vista del panel de administración
está sin representar y es la mitad menos obvia del proyecto.

## Qué debería corregirse en la ficha actual

La ficha describe el proyecto como una página de contenido. **Tiene panel de
administración con autenticación real, CRUD con subida de archivos y una lista de
medidas de seguridad concreta.** Es más de lo que dice.

---

# 8. GoodMovies

- **Carpeta fuente**: `C:\xampp\htdocs\goodmoviesproyecto`
- **Repositorio**: `https://github.com/cp327/goodmoviesproyecto`
- **Periodo**: etapa de formación en el **SENA** (Tecnólogo en análisis y
  desarrollo de software, 2021–2023)
- **En el portafolio**: publicado como proyecto **05 / 05**

## Contexto

Proyecto de formación. El objetivo era **afianzar y poner en práctica** lo
aprendido construyendo algo completo: una plataforma de películas inspirada en la
experiencia de un servicio de streaming.

## Arquitectura — tres áreas por rol

La estructura revela la intención pedagógica: **el mismo sistema visto desde tres
roles distintos**.

```
src/
├── auth/     → registro, login, verificación, compra, factura
├── app/      → área del usuario suscrito
├── admin/    → gestión del catálogo de películas
├── core/     → back-office: empleados, clientes, estados
├── config/   → conexión
└── public/   → css, js, libs (Bootstrap)
```

Cada área repite el patrón `models/` (PHP que toca la base) + `views/` (la
pantalla) + `controllers/` (el JavaScript que las conecta). Es MVC hecho a mano,
sin framework — que es exactamente lo que se aprende en esa etapa.

## Funcionalidades verificadas

**Área de usuario** (`src/app/`):
catálogo por categorías (acción, aventura, drama, terror) · **búsqueda** ·
**favoritos** con alta, baja y verificación · **descargas** con alta, baja y
verificación · ajustes de cuenta con cambio de contraseña.

**Área de administración** (`src/admin/`):
CRUD completo de películas (agregar, actualizar, eliminar) · vistas por categoría ·
búsqueda · generación de descripción.

**Back-office** (`src/core/`):
gestión de empleados (alta, actualización, baja) · consulta de clientes ·
gestión de estado · tabla con funciones propias.

**Autenticación y suscripción** (`src/auth/`):
registro · verificación · login · **flujo de compra con factura** — simulado,
sin pagos reales.

## Modelo de datos

Base `goodmovies` en MySQL. Cuatro tablas:

| Tabla | Campos destacables |
|---|---|
| `usuarios` | nombres, apellidos, correo, `fyh_creacion`, **`rol`**, `estado`, **`membresia_inicio`**, **`membresia_expiracion`** |
| `peliculasgm` | título, categoría, sinopsis, **`IMGpORTADA` y `IMGfONDO` como `longblob`**, vídeo |
| `favoritos` | usuario ↔ película |
| `descargas` | usuario ↔ película |

Dos observaciones honestas sobre el esquema, que son buen material para hablar de
aprendizaje:

- **Las imágenes se guardan como `longblob` dentro de la base.** Funciona, pero
  hoy irían al disco con la ruta en la tabla: los blobs inflan los backups y no
  se pueden servir con caché.
- La **membresía vive en la propia tabla de usuarios** (`membresia_inicio` /
  `membresia_expiracion`), sin historial de suscripciones. Suficiente para el
  alcance del ejercicio; insuficiente para renovaciones.

Poder señalar esto es más valioso que ocultarlo: demuestra que la distancia entre
ese proyecto y AG Identity se recorrió de verdad.

## Tecnologías verificadas

PHP · MySQL · JavaScript · HTML5 · CSS3 · **Bootstrap** (incluido localmente en
`src/public/libs/`) · hojas responsive separadas por vista
(`styles_*_responsive.css`) · animaciones propias (`starsAnimation.js`).

## Estado actual

Demo pública.

## Evidencia visual

Ya en el portafolio: `gm1.png` … `gm6.png` (6 capturas). **No hacen falta
capturas nuevas.**

## Qué representa en la evolución

El punto de partida. Es el proyecto que fija la línea base contra la que se mide
todo lo demás: la misma persona que guardaba imágenes como blob en MySQL cinco
años después calibra un umbral biométrico con mediciones propias contra el
hardware.

---

# Verificaciones pendientes

Preguntas que **no se pueden resolver leyendo el código** y que hay que confirmar
con Camilo antes de escribir nada en el portafolio.

## Resueltas — 20 de agosto de 2026

| Proyecto | Pregunta | Decisión de Camilo |
|---|---|---|
| **WhatsApp** | El recuerdo hablaba de facturas y vencimientos; el código lee un Google Calendar | **Se documenta solo lo que respalda el código**: la integración Calendar → WhatsApp. Nada de facturas ni de períodos |
| **AG Identity** | Reparto real del trabajo | **Desarrollo conjunto de dos personas, presencial.** Ambos en backend y frontend, divididos por ramas; los dos conocen el código completo. Los commits **no** reflejan el reparto |
| **ArgosMonitors** | Reparto real del trabajo | Igual que arriba. El **rediseño del panel** sí es individualmente atribuible |
| **ArgosMonitors** | ¿Nombrar al fabricante y al cliente de la demo? | **No se nombra a ninguno.** Ni nombres ni NIT, ni aquí ni en el portafolio |
| **Southern Roofing** | No hay repositorio git | **Sin botón "Ver el código".** La ficha lleva solo "Visitar el sitio", que además es su mejor prueba |

## Abiertas

| # | Proyecto | Qué falta confirmar | Por qué importa |
|---|---|---|---|
| 1 | **AG Identity / ArgosMonitors** | Ambos repositorios pertenecen a la cuenta del compañero de proyecto y son privados. Los botones «Código» ya apuntan ahí, así que **a un visitante sin acceso le saldrá un 404** | Camilo pidió dejar el enlace aunque estén privados. Queda decidir si eso se mantiene o si se retira el botón, como se hizo en Southern Roofing |
| 2 | **AG Identity** | Falta la captura del **enrolamiento con el agente activo**, que exige el lector FS88 conectado | Es la única pantalla que enseñaría el puente navegador → agente → lector, que es la parte más singular del sistema |
| 3 | **Southern Roofing** | Montar el **antes y después** con los `vista-*-old.html` de la carpeta fuente | Sería la pieza más convincente del proyecto y ningún otro puede ofrecerla |
| 4 | **AgroIA** | ¿Dónde está desplegado? El modelo (`.pkl`) y el CSV limpio **no están en el repositorio**, así que un clon no arranca | La ficha dice "En línea, con credenciales de prueba" |
| 5 | **AgroIA** | Reparto de trabajo del equipo académico | Mismo criterio que en los otros proyectos en pareja |
| 6 | **B&B** | Existen dos repositorios (`cp327/BBPFTO` y `cp327/BBPFTOProyecto`) con el mismo contenido | Ruido en el perfil de GitHub. Conviene archivar uno |
| 7 | **B&B** | El volcado `bybpro.sql` del repositorio conserva datos de prueba con **nombres de empresas reales** | No son secretos, pero son datos de terceros en un repositorio público |
| 8 | **AG Identity** | El README del proyecto fuente sigue diciendo «178 pruebas», cifra anterior a la fase de competición | No afecta al portafolio, pero conviene avisar al equipo |

## Cómo volver a capturar

Los dos proyectos destacados se levantan en local así. **Ninguno de estos pasos
modifica código fuente**; el único que toca datos es `migrate`, y ya está hecho.

```bash
# MySQL de XAMPP (si no está corriendo)
C:/xampp/mysql/bin/mysqld.exe --defaults-file=C:/xampp/mysql/bin/my.ini --standalone

# AG Identity → http://localhost:8000  (panel en /admin)
cd C:/xampp/htdocs/AG-IDENTIFY/Backend
C:/xampp/php/php.exe artisan serve --host=127.0.0.1 --port=8000

# ArgosMonitors → http://localhost:8001
# Necesita las DOS cosas: el proyecto está en modo Vite dev (existe public/hot)
# y sin el servidor de assets la página sale completamente en blanco.
cd C:/xampp/htdocs/ArgosRisk
C:/xampp/php/php.exe artisan serve --host=127.0.0.1 --port=8001
npm run dev
```

Bases de datos: `ag_identify` y `argosrisk`, ambas con datos de prueba.
Copia de seguridad previa a la migración de AG en el scratchpad de la sesión:
`ag_identify_backup_pre_migrate.sql`.

**Antes de publicar cualquier captura de ArgosMonitors**, sustituir el nombre
del cliente en el DOM (aparece en la barra lateral, en el subtítulo del
escritorio y en los correos de los empleados).

---

# Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-08-20 | Creación. Investigación inicial de los ocho proyectos leyendo código, dependencias, migraciones, rutas, documentación interna e historial de git. Detectados cuatro conflictos entre el recuerdo y el código: base de datos de AG Identity (MySQL, no PostgreSQL), alcance del proyecto de WhatsApp (calendario, no facturas), naturaleza de Southern Roofing (rediseño de WordPress inyectado con WPCode, no landing nueva) y librerías de SITI Colombia (sin Select2; con DataTables, Chart.js y Font Awesome) |
| 2026-08-20 | **Revalidación de AG Identity** tras actualizar la rama a `main` (44 commits). Incorporada la **fase de competición v2.5**, que no estaba en la primera lectura: 11 tablas nuevas, 7 enums, recursos de panel para fases, partidos, sanciones y cuarentena, endpoint `POST /actas/eventos`, matching contra plantilla con búsqueda en dos pasos, ruta de excepción con tope, cierre de acta y resolución de conflicto entre máquinas. Conteo de pruebas corregido de 178 (cifra obsoleta del README) a ~384 casos en 38 archivos |
| 2026-08-20 | Cerradas cinco decisiones con Camilo: alcance del proyecto de WhatsApp, participación en AG Identity y ArgosMonitors, anonimato del cliente de ArgosMonitors y ausencia de botón de código en Southern Roofing. Retirados del documento los nombres de fabricante y cliente |
| 2026-08-20 | **20 capturas reales** tomadas levantando los proyectos en local (8 de AG Identity, 8 de ArgosMonitors, 4 de Southern Roofing desde el sitio en vivo). Para AG hubo que aplicar 13 migraciones pendientes, con autorización y copia de seguridad previa; para Argos, levantar el servidor de Vite. Las de Argos van anonimizadas |
| 2026-08-20 | **Implementado en el portafolio**: dos niveles de proyecto (cuatro destacados en filas, cuatro en lista con reglas), tres páginas de caso nuevas, renumeración a `/08`, navegación circular entre las ocho, `sitemap.xml` ampliado y con el espacio de nombres corregido, y `Laravel`, `React`, `TypeScript` y `.NET` añadidos a las habilidades y al JSON-LD |
