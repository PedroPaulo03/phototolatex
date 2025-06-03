import streamlit as st 
import numpy as np # Importa numpy para EasyOCR
from google import genai
from google.genai import types

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Notas para LaTeX",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✍️ Transforme Notas Manuscritas em markdown")
 
INSTRUCOES = """
Você é um assistente de IA que converte texto de anotações manuscritas em formato markdown.
Seu objetivo é representar o texto com precisão, prestando atenção especial às equações matemáticas.
- Identifique expressões matemáticas e as envolva em `$` para equações inline ou `$$` para equações de exibição.
Exemplo: `E=mc^2` deve se tornar `$E=mc^2$`
`integral de a a b f(x) dx` deve se tornar `$$\int_a^b f(x) dx$$`
 - Preserve quebras de parágrafo.
- Não inclua quaisquer observações introdutórias ou conclusivas, apenas o código markdown puro."""

  


def generate(imagem_bytes):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    modelo = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="image/png",
                    data=imagem_bytes,
                ), 
                types.Part.from_text(text=INSTRUCOES),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    resposta = client.models.generate_content(
        model = modelo,
        contents = contents,
        config = generate_content_config,
    )

    return resposta.text
 
 


imagem_carregada = st.file_uploader(
    "Selecione uma imagem (.png, .jpeg, .jpg) )",
    type=["png", "jpeg", "jpg"],
    accept_multiple_files=False # Para este exemplo, apenas um arquivo por vez
)

col1, col2 = st.columns(2)

if imagem_carregada is not None:
    with col1:
        st.subheader("Pré-visualização da Imagem:")
        # Exibe a imagem carregada. Para PDF, mostrará apenas a primeira página.
        st.image(imagem_carregada, caption="Sua imagem carregada")#, width =300)

    st.markdown("---")
    with col2:  
        if st.button("Processar Imagem e Gerar LaTeX", key="process_button"):
            # Garante que o arquivo foi carregado antes de processar
            if imagem_carregada.getvalue():
    
                with st.spinner("Convertendo texto para LaTeX...", show_time=True):
                    file_bytes = imagem_carregada.getvalue()

                    try: 
                        saida = generate(file_bytes)
                    except Exception as e:
                        st.error(f"Erro ao processar a imagem: {e}")
                        
                st.markdown("---")
                st.subheader("Resultado em LaTeX:")             
                st.markdown(saida)
                st.code(saida)

            else:
                st.warning("Nenhum arquivo válido foi carregado para processamento.")
else:
    st.info("Por favor, carregue uma imagem ou um arquivo PDF para começar.")

 
