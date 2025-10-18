# API layer structure

En este directorio están los modulos de API para cada recurso, a partir de HTTP client (en ../httpClient)
- httpClient.js: configuración de URL, auth header, manejo de JSON/FormData, normalización de errores
- usuarios.js: login, register, list, getById, update
- equipos.js: register, list, getById, update
- ligas.js: list, getById
- media.js: getEquipoMedia, uploadEquipoImage

Uso recomendado (importaciones directas por recurso):

```
// Ejemplos reales desde el código de la app:
// - Desde src/context/authContext.js
import { login } from '../utils/communicationModule/resources/usuarios'

// - Desde src/pages/usuario/*.js
import { list as listEquipos } from '../../utils/communicationModule/resources/equipos'
import { list as listUsuarios } from '../../utils/communicationModule/resources/usuarios'
import { list as listLigas } from '../../utils/communicationModule/resources/ligas'

// - Media (subida de imagen y obtener media de equipo)
import { uploadEquipoImage, getEquipoMedia } from '../../utils/communicationModule/resources/media'

// Uso
await login({ correo, contrasena })
const equipos = await listEquipos()
const ligas = await listLigas()
```

Environment variables:
- REACT_APP_API_BASE_URL (default: http://localhost:8000)
- REACT_APP_API_BASE_PATH (default: /api)