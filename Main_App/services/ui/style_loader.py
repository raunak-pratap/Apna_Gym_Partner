from pathlib import Path
import base64

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "static"


def load_css(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        return

    with file_path.open("r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )


def inject_local_font(font_path, font_name):
    font_path = Path(font_path)

    if not font_path.exists():
        return

    with font_path.open("rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    ext = font_path.suffix.lstrip(".")
    fmt = {"otf": "opentype"}.get(ext, ext)
    mime = {"otf": "font/otf"}.get(ext, f"font/{ext}")

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: "{font_name}";
            src: url("data:{mime};base64,{encoded}") format("{fmt}");
            font-weight: 100 900;
            font-style: normal;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_webrtc_styles():
    font_path = STATIC_DIR / "AdobeClean.otf"

    if not font_path.exists():
        return

    with font_path.open("rb") as font_file:
        encoded_font = base64.b64encode(font_file.read()).decode()

    try:
        components.html(
            f"""
            <script>
            (function patchWebRTCStyles() {{

                function injectIntoIframe(iframe) {{
                    try {{
                        const doc = iframe.contentDocument || iframe.contentWindow.document;

                        if (!doc || !doc.head) return;

                        if (doc.head.querySelector("#webrtc-custom-styles")) return;

                        const style = doc.createElement("style");
                        style.id = "webrtc-custom-styles";

                        style.textContent = `
                            @font-face {{
                                font-family: "AdobeClean";
                                src: url("data:font/otf;base64,{encoded_font}") format("opentype");
                                font-weight: 100 900;
                                font-style: normal;
                            }}

                            .MuiButtonBase-root,
                            .MuiButton-root,
                            .MuiButton-contained,
                            .MuiButton-text {{
                                border-radius: 0 !important;
                                font-family: "AdobeClean", sans-serif !important;
                                letter-spacing: 0.05em !important;
                            }}
                        `;

                        doc.head.appendChild(style);

                    }} catch (e) {{
                        console.warn("WebRTC style injection failed:", e);
                    }}
                }}

                function patchIframes() {{
                    const parentDoc = window.parent.document;
                    const iframes = parentDoc.querySelectorAll("iframe");

                    iframes.forEach((iframe) => {{
                        if (
                            iframe.src &&
                            iframe.src.includes("webrtc")
                        ) {{
                            if (
                                iframe.contentDocument &&
                                iframe.contentDocument.readyState === "complete"
                            ) {{
                                injectIntoIframe(iframe);
                            }} else {{
                                iframe.addEventListener(
                                    "load",
                                    () => injectIntoIframe(iframe)
                                );
                            }}
                        }}
                    }});
                }}

                patchIframes();

            }})();
            </script>
            """,
            height=0,
        )

    except Exception as e:
        st.warning(f"Unable to inject WebRTC styles: {e}")
