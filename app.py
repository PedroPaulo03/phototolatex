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

st.title("✍️ Transforme Notas Manuscritas em LaTeX")
 
INSTRUCOES = """
Você é um assistente de IA que converte texto de anotações manuscritas em formato LaTeX.
Seu objetivo é representar o texto com precisão, prestando atenção especial às equações matemáticas.
- Identifique expressões matemáticas e as envolva em `$` para equações inline ou `$$` para equações de exibição.
Exemplo: `E=mc^2` deve se tornar `$E=mc^2$`
`integral de a a b f(x) dx` deve se tornar `$$\int_a^b f(x) dx$$`
 - Preserve quebras de parágrafo.
- Não inclua quaisquer observações introdutórias ou conclusivas, apenas o código LaTeX puro."""

  


def generate(imagem_bytes, type):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    modelo = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type=type,
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


INSTRUCOES_LATEX = """
A partir do texto que vou fornecer, estruture um código LaTeX com uma formatação limpa,
organizada e visualmente agradável (seguindo boas práticas de formatação de documentos).
Não deve modificar o conteúdo do texto de forma alguma.
A saída deve ser todo esse texto em LaTeX completo, pronto para compilar.
Não coloque nenhum texto adicional, apenas o código LaTeX. Não use ```latex antes do texto e nem ``` no final.
Use uma estrutura básica de documento LaTeX, incluindo:
- `\documentclass{article}`
"""

def estruturar_latex(texto: str) -> str:
    """
    Recebe um texto bruto e retorna um código LaTeX completo,
    sem alterar o conteúdo, apenas adicionando toda a estrutura
    (documentclass, pacotes, seções, etc.) de forma organizada.
    """
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    model = "gemini-2.5-flash-preview-05-20"

    # monta o conteúdo do prompt, unindo instruções e seu texto
    combined_prompt = f"{INSTRUCOES_LATEX}\n\nTexto de entrada:\n{texto}"

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=combined_prompt)]
        )
    ]

    config = types.GenerateContentConfig(
        response_mime_type="text/plain"
    )

    # faz a chamada e já pega a resposta toda
    resposta = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return resposta.text


imagens_carregadas = st.file_uploader(
    "Selecione uma imagem (.png, .jpeg, .jpg) )",
    type=["png", "jpeg", "jpg"],
    accept_multiple_files=True # Para este exemplo, apenas um arquivo por vez
)

col1, col2 = st.columns(2)

with col1:
    st.subheader('Pré-visualização da imagem')
    imagem_visualizada = st.selectbox(label='Selecione a imagem para pré-visualização',
                                       format_func=lambda img: img.name if img else "Arquivo desconhecido",
                                      options = imagens_carregadas, index = 0)
    if imagem_visualizada is not None:
        imagem_bytes = imagem_visualizada.getvalue()
        st.image(imagem_bytes, caption="Imagem selecionada", use_container_width=True)


# if imagens_carregadas is not None:
#     with col1:
#         st.subheader("Pré-visualização da Imagem:")
#         # Exibe a imagem carregada. Para PDF, mostrará apenas a primeira página.
#         st.image(imagens_carregadas, caption="Sua imagem carregada")#, width =300)

with col2:
    if imagens_carregadas and len(imagens_carregadas) > 0:  
        if st.button("Processar Imagem e Gerar LaTeX", key="process_button"):
            # Garante que o arquivo foi carregado antes de processa
            saidas = ''  # Variável para armazenar as saídas LaTeX
            for i, imagem_carregada in enumerate(imagens_carregadas):
                
                if imagem_carregada.getvalue():
                    
                    with st.spinner(f"Convertendo texto da página {i+1} para LaTeX...", show_time=True):
                        file_bytes = imagem_carregada.getvalue()
                        try: 
                            saida = generate(file_bytes, type=imagem_carregada.type)
                            saidas += saida + "\n\n"
                        except Exception as e:
                            st.error(f"Erro ao processar a imagem: {e}")
                                
                else:
                        st.warning("Nenhum arquivo válido foi carregado para processamento.")

            # Exibir o resultado em LaTeX
            st.markdown("---")
            st.subheader("Resultado em LaTeX:")             
            # st.markdown(saidas)
            st.code(saidas)
            # Baixar o resultado em LaTeX
            saida_final = estruturar_latex(saidas)

            st.download_button(
                label="Baixar código LaTeX",
                data=saida_final,            # sua string de texto
                file_name="relatorio.txt",   # extensão .txt
                mime="text/plain",           
            )
    else:
        st.info("Por favor, carregue uma imagem ou um arquivo PDF para começar.")


 