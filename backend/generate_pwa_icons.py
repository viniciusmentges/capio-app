import os
import sys
import subprocess

def install_pillow():
    try:
        from PIL import Image, ImageOps
        print("Pillow já está instalado.")
    except ImportError:
        print("Pillow não encontrado. Instalando Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

def generate_icons():
    from PIL import Image

    base_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.abspath(os.path.join(base_dir, "..", "frontend", "public"))
    favicon_path = os.path.join(public_dir, "favicon.png")

    if not os.path.exists(favicon_path):
        print(f"Erro: Favicon não encontrado em {favicon_path}")
        return

    print(f"Abrindo favicon original de: {favicon_path}")
    img = Image.open(favicon_path)

    # 1. Gerar pwa-192x192.png
    pwa_192_path = os.path.join(public_dir, "pwa-192x192.png")
    img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    img_192.save(pwa_192_path, "PNG")
    print(f"Criado: {pwa_192_path}")

    # 2. Gerar pwa-512x512.png
    pwa_512_path = os.path.join(public_dir, "pwa-512x512.png")
    img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    img_512.save(pwa_512_path, "PNG")
    print(f"Criado: {pwa_512_path}")

    # 3. Gerar apple-touch-icon.png (180x180)
    apple_path = os.path.join(public_dir, "apple-touch-icon.png")
    img_apple = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_apple.save(apple_path, "PNG")
    print(f"Criado: {apple_path}")

    # 4. Gerar maskable-icon-512x512.png com margem de segurança e fundo off-white da CAPIO (#F8F7F4)
    # De acordo com as diretrizes do W3C, a imagem maskable deve ter uma margem de segurança.
    # Colocamos o logotipo centralizado com cerca de 70% do tamanho total (360px) em um canvas de 512x512.
    maskable_path = os.path.join(public_dir, "maskable-icon-512x512.png")
    
    # Criar um fundo sólido com a cor oficial da CAPIO (#F8F7F4)
    background_color = (248, 247, 244, 255) # RGB para #F8F7F4
    maskable_canvas = Image.new("RGBA", (512, 512), background_color)
    
    # Redimensionar o favicon para caber na zona segura (360x360)
    logo_size = 360
    logo_resized = img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Se o favicon original tiver transparência, a colagem com canal alfa é preservada
    if logo_resized.mode in ('RGBA', 'LA') or (logo_resized.mode == 'P' and 'transparency' in logo_resized.info):
        # Centralizar a colagem
        offset = ((512 - logo_size) // 2, (512 - logo_size) // 2)
        maskable_canvas.alpha_composite(logo_resized.convert("RGBA"), dest=offset)
    else:
        # Colagem simples para imagens sem canal alfa
        offset = ((512 - logo_size) // 2, (512 - logo_size) // 2)
        maskable_canvas.paste(logo_resized, offset)
        
    maskable_canvas.save(maskable_path, "PNG")
    print(f"Criado Ícone Maskable Premium: {maskable_path}")
    print("Todos os ícones PWA foram gerados com sucesso!")

if __name__ == "__main__":
    install_pillow()
    generate_icons()
