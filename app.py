import streamlit as st
import replicate
import os
import requests
from io import BytesIO

# --- Configuración Inicial ---
st.set_page_config(page_title="Generador de Imágenes Flux Pro", layout="centered")
st.title("🎨 Generador de Imágenes con Flux Pro")
st.caption("Usando el modelo black-forest-labs/flux-1.1-pro en Replicate.")

# --- Obtener API Key de Replicate ---
# Intenta obtener la API key desde los secretos de Streamlit (si se despliega allí)
# o desde las variables de entorno (para Cloud Run u otros)
replicate_api_key =  os.environ.get("REPLICATE_API_TOKEN")

if not replicate_api_key:
    st.error("🛑 La API Key de Replicate no está configurada.")
    st.info("Asegúrate de configurar la variable de entorno 'REPLICATE_API_TOKEN' en tu despliegue de Cloud Run.")
    st.stop() # Detiene la ejecución si no hay API key

# Asigna la API key a Replicate (aunque el cliente también la busca en la variable de entorno por defecto)
# os.environ["REPLICATE_API_TOKEN"] = replicate_api_key # No es estrictamente necesario si la variable ya está en el entorno

# --- Interfaz de Usuario ---
with st.form("image_generation_form"):
    prompt = st.text_area(
        "✍️ Introduce el prompt para la imagen:",
        height=100,
        placeholder="Ej: Un astronauta montando un caballo en la luna, estilo fotorrealista."
    )
    # El modelo usa 'seed' para la aleatoriedad, no 'temperature' directamente.
    # Usaremos el slider para controlar el 'seed'.
    seed = st.slider(
        "🌱 Semilla (Seed) - Afecta la aleatoriedad:",
        min_value=0,
        max_value=100000, # Puedes ajustar el máximo si quieres más rango
        value=42, # Valor por defecto del ejemplo
        help="Cambia este valor para obtener variaciones de la misma imagen."
    )
    # Mantenemos otros parámetros fijos según el ejemplo, podrías añadirlos a la UI si quieres
    aspect_ratio = "1:1"
    output_format = "jpg" # Formato de salida
    output_quality = 80

    submitted = st.form_submit_button("🚀 Generar Imagen")

# --- Lógica de Generación y Visualización ---
if submitted:
    if not prompt:
        st.warning("⚠️ Por favor, introduce un prompt para generar la imagen.")
    elif not replicate_api_key:
         st.error("🛑 Falta la API Key de Replicate. Configura la variable de entorno.")
    else:
        st.markdown("---")
        st.info(f"⏳ Generando imagen con el prompt: '{prompt}' y seed: {seed}...")
        try:
            with st.spinner('Llamando a la API de Replicate... esto puede tardar un poco...'):
                # Llamada a la API de Replicate
                # Usamos la versión específica del modelo para mayor estabilidad
                model_version = "black-forest-labs/flux-1.1-pro"
                output = replicate.run(
                    model_version,
                    input={
                        "seed": seed,
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "output_format": output_format,
                        "output_quality": output_quality,
                        "safety_tolerance": 2.0, # Asegúrate de que sea float si el modelo lo requiere
                        "prompt_upsampling": True
                    }
                )
            print(output)
            print(dir(output))
            # --- Procesamiento de la Salida ---
            image_url = output.url # Inicializamos la variable

            # # Verificamos si la salida es directamente una URL (string) válida
            # if output and isinstance(output, str) and output.startswith("http"):
            #      image_url = output
            # # Verificamos si la salida es una lista y el primer elemento es una URL válida
            # elif output and isinstance(output, list) and len(output) > 0 and isinstance(output[0], str) and output[0].startswith("http"):
            #      image_url = output[0]

            # Si hemos conseguido una URL válida, la mostramos y damos opción a descargar
            if image_url:
                st.success("✅ ¡Imagen generada con éxito!")
                st.image(image_url, caption=f"Imagen generada para: '{prompt}'")

                # --- Descarga de la Imagen ---
                try:
                    st.info("Descargando imagen para el botón...")
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status() # Lanza excepción si hay error HTTP (4xx o 5xx)

                    # Prepara los datos para el botón de descarga
                    image_bytes = BytesIO(response.content)
                    file_extension = output_format # Ya lo definimos antes

                    st.download_button(
                        label=f"📥 Descargar Imagen ({file_extension.upper()})",
                        data=image_bytes,
                        file_name=f"generated_image_{seed}.{file_extension}",
                        mime=f"image/{file_extension}" # Mime type correcto para webp
                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error al descargar la imagen desde la URL: {e}")
                except Exception as e_download:
                     st.error(f"❌ Ocurrió un error durante la preparación de la descarga: {e_download}")


            # Si después de las comprobaciones no tenemos una URL válida
            else:
                st.error("❌ La API de Replicate no devolvió una URL de imagen válida o en un formato esperado.")
                st.write("Respuesta recibida por la API:", output) # Mostramos lo que llegó para depurar

        except replicate.exceptions.ReplicateError as e:
            # Errores específicos de la API de Replicate (e.g., key inválida, modelo no encontrado, error interno de Replicate)
            st.error(f"❌ Error en la API de Replicate: {e}")
        except requests.exceptions.RequestException as e:
             # Errores de red al intentar conectar con Replicate
             st.error(f"❌ Error de conexión al llamar a Replicate: {e}")
        except Exception as e:
            # Captura cualquier otro error inesperado
            st.error(f"❌ Ocurrió un error inesperado durante la generación: {e}")
            st.error(f"Tipo de error: {type(e).__name__}")


st.markdown("---")
st.markdown("Creado con [Streamlit](https://streamlit.io) y [Replicate](https://replicate.com)")