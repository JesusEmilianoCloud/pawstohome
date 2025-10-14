Setup de proveedores sociales (Google y Facebook) para Django Allauth

Resumen rápido

- Google ya está configurado como provider en `settings.py`.
- Se agregó `allauth.socialaccount.providers.facebook` a `INSTALLED_APPS`.
- Debes crear una SocialApp en el admin de Django (Sitios > Social applications) para cada provider y enlazarlo al `SITE_ID` correcto.

Pasos para configurar Facebook (en local o producción):

1. Crear una app en Facebook for Developers:
   - Visita https://developers.facebook.com/ y crea una nueva app.
   - Agrega el producto "Facebook Login" y configura la URL de redirección.
   - En Settings > Basic obtén el `App ID` y `App Secret`.

2. Configurar en Django admin:
   - Inicia el servidor y entra al admin: `/admin/`.
   - Ve a "Social applications" (Allauth) y crea una nueva SocialApp:
       - Provider: Facebook
       - Name: Facebook (o el nombre que prefieras)
       - Client id: App ID de Facebook
       - Secret key: App Secret de Facebook
       - Key: (dejar vacío)
       - Sites: Selecciona el `Site` correspondiente (relacionado a `SITE_ID` en settings)

3. Variables de entorno recomendadas (opcional):
   - FACEBOOK_CLIENT_ID
   - FACEBOOK_SECRET

4. `settings.py` relevantes:
   - Asegúrate de tener `allauth.socialaccount.providers.facebook` en `INSTALLED_APPS`.
   - `SOCIALACCOUNT_PROVIDERS['facebook']` contiene `SCOPE` y `FIELDS` necesarios.

5. URLs:
   - Allauth ya está incluido en `pawtohome/urls.py` con `path('auth/', include('allauth.urls'))`.
   - En la plantilla, usa `{% provider_login_url 'facebook' %}` para obtener la URL correcta.

Notas:
- Para producción asegúrate de configurar correctamente los dominios válidos en la app de Facebook y usar HTTPS.
- Si usas entorno local con `localhost`, Facebook puede requerir ngrok o un dominio público para probar el OAuth redirect.

Si quieres, puedo crear automáticamente variables de entorno en `.env.example` y un `manage.py` command para validar que las SocialApps están registradas.