from flask import Flask, request, send_file, jsonify
import hashlib
from PIL import Image
import io

app = Flask(__name__)

@app.route("/")
def init_test():
    return "Está conectado!"

@app.route('/calcula-hash', methods=['POST'])
def calcula_hash():
    if 'file' not in request.files: 
        return {'error': 'Nenhum arquivo enviado'}, 400
    
    file = request.files['file']
    nome_original = request.form.get('nomeOriginal', '')

    if file.filename == '':
        return {'error': 'Nenhum arquivo selecionado'}, 400
    
    try:
        file_conteudo = file.read();
    
        md5_hash = hashlib.md5(file_conteudo).hexdigest()
        sha256_hash = hashlib.sha256(file_conteudo).hexdigest()
        sha1_hash = hashlib.sha1(file_conteudo).hexdigest()
        sha384_hash = hashlib.sha384(file_conteudo).hexdigest()

        return jsonify({
            'Nome do arquivo': nome_original if nome_original else file.filename,
            'hashes': {
                'md5': md5_hash,
                'sha256': sha256_hash,
                'sha1': sha1_hash,
                'sha384': sha384_hash
            }
        })
    
    except Exception as e:
        print("Erro:", str(e))
        return {'error': str(e)}, 500
    
@app.route('/calcula-pixels', methods=['POST'])
def calcula_pixels():
    if 'file' not in request.files:
        return {'error': 'Nenhum arquivo enviado'}, 400
    
    file = request.files['file']
    nome_original = request.form.get('nomeOriginal', '')

    if file.filename == '':
        return {'error': 'Nenhum arquivo selecionado'}, 400
        
    try:
        imagem = Image.open(file)
        largura, altura = imagem.size
        total_pixels = largura * altura
        
        return jsonify({
            'Nome do arquivo': nome_original if nome_original else file.filename,
            'dimensões': {
                'width': f"{largura}px",
                'height': f"{altura}px"
            },
            'total de pixels': total_pixels,
        })
        
    except Exception as e:
        print("Erro:", str(e))
        return {'error': str(e)}, 500
    
@app.route('/redimensiona-imagem', methods=['POST'])
def redimensiona_imagem():
    if 'file' not in request.files:
        return {'error': 'Nenhum arquivo enviado'}, 400
    
    largura = request.form.get('largura', type=int)
    altura = request.form.get('altura', type=int)
    
    if not largura or not altura:
        return {'error': 'Largura e altura são obrigatórios'}, 400
    
    file = request.files['file']
    
    if file.filename == '':
        return {'error': 'Nenhum arquivo selecionado'}, 400
        
    try:
        image = Image.open(file)
        resized_image = image.resize((largura, altura), Image.Resampling.LANCZOS)
        
        img_byte_array = io.BytesIO()
        resized_image.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        return send_file(
            img_byte_array,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'imagem_redimensionada_{largura}x{altura}.png'
        )
        
    except Exception as e:
        print("Erro:", str(e))
        return {'error': str(e)}, 500
    
@app.route('/compara-hashes', methods=['POST'])
def compare_hashes():
    if 'file1' not in request.files or 'file2' not in request.files:
        return {'error': 'São necessários dois arquivos (file1 e file2)'}, 400
    
    file1 = request.files['file1']
    nome_original1 = request.form.get('nomeOriginal1', '')
    file2 = request.files['file2']
    nome_original2 = request.form.get('nomeOriginal2', '')
    
    if file1.filename == '' or file2.filename == '':
        return {'error': 'Dois arquivos devem ser selecionados'}, 400
        
    try:
        content1 = file1.read()
        content2 = file2.read()
        
        hashes1 = {
            'md5': hashlib.md5(content1).hexdigest(),
            'sha256': hashlib.sha256(content1).hexdigest(),
            'sha1': hashlib.sha1(content1).hexdigest(),
            'sha384': hashlib.sha384(content1).hexdigest()
        }
        
        hashes2 = {
            'md5': hashlib.md5(content2).hexdigest(),
            'sha256': hashlib.sha256(content2).hexdigest(),
            'sha1': hashlib.sha1(content2).hexdigest(),
            'sha384': hashlib.sha384(content2).hexdigest()
        }
        
        comp = {
            'md5': hashes1['md5'] == hashes2['md5'],
            'sha1': hashes1['sha1'] == hashes2['sha1'],
            'sha256': hashes1['sha256'] == hashes2['sha256']
        }
        
        return jsonify({
            'files': {
                'file1': nome_original1 if nome_original1 else file1.filename,
                'file2': nome_original2 if nome_original2 else file2.filename,
            },
            'hashes': {
                'file1': hashes1,
                'file2': hashes2
            },
            'Comparação': comp,
            'São identicos': all(comp.values())
        })
        
    except Exception as e:
        print("Erro:", str(e))
        return {'error': str(e)}, 500
    
@app.route('/filtro-imagem', methods=['POST'])
def filtro_imagem():

    if 'file' not in request.files:
        return {'error': 'Nenhum arquivo enviado'}, 400
    
    file = request.files['file']
    
    if file.filename == '':
        return {'error': 'Nenhum arquivo selecionado'}, 400
        
    try:
        image = Image.open(file)
        processed_image = image.convert('L')
        
        img_byte_array = io.BytesIO()
        processed_image.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        return send_file(
            img_byte_array,
            mimetype='image/png',
            as_attachment=True,
            download_name='imagem_cinza.png'
        )
        
    except Exception as e:
        print("Erro:", str(e))
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)