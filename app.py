from flask import Flask, app, flash, jsonify, render_template, request, redirect, url_for
from config import Config
from extensions import db
from datetime import datetime
from models import ProdutoAcao  # certifique-se de importar no topo com os outros modelos
from models import SubacaoEntrega  # certifique-se de importar no topo com os outros modelos
from models import MunicipioEntrega
from flask import session

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
        from models import Programa, Acao  # ✅ Importamos também o modelo Acao
        db.create_all()

        @app.route('/')
        def home():
            return render_template('home.html')

        @app.route('/cadastrar')
        def cadastrar_pta():
            programas = Programa.query.filter_by(ativo=True).all()
            return render_template('cadastrar_programa.html', programas=programas)

        @app.route('/excluir_programa/<int:id>', methods=['POST'])
        def excluir_programa(id):
            programa = Programa.query.get(id)
            if programa:
                programa.ativo = False
                programa.excluido_em = datetime.now()
                db.session.commit()
            return redirect(url_for('cadastrar_pta'))

        @app.route('/inserir_programa', methods=['POST'])
        def inserir_programa():
            programa_id = request.form.get('programa_id')

            nome = request.form['nome']
            funcao = request.form['funcao']
            responsavel = request.form['responsavel']
            cpf = request.form['cpf']
            email = request.form['email']

            if programa_id:
                # Atualização
                programa = Programa.query.get(int(programa_id))
                if programa:
                    programa.nome = nome
                    programa.funcao = funcao
                    programa.responsavel = responsavel
                    programa.cpf = cpf
                    programa.email = email
                    programa.alterado_em = datetime.now()
            else:
                # Novo cadastro
                novo_programa = Programa(
                    nome=nome,
                    funcao=funcao,
                    responsavel=responsavel,
                    cpf=cpf,
                    email=email,
                    ativo=True
                )
                db.session.add(novo_programa)

            db.session.commit()
            return redirect(url_for('cadastrar_pta'))

        @app.route('/acoes/<int:programa_id>')
        def acoes_por_programa(programa_id):
            programa = Programa.query.get_or_404(programa_id)
            acoes = Acao.query.filter_by(programa_id=programa_id, ativo=True).all()
            return render_template('cadastrar_acao.html', programa=programa, acoes=acoes)

        @app.route('/inserir_acao', methods=['POST'])
        def inserir_acao():
            programa_id = request.form.get('programa_id')
            acao_id = request.form.get('acao_id')  # para edição futura

            subfuncao = request.form['subfuncao']
            acao_paoe = request.form['acao_paoe']
            responsavel = request.form['responsavel']
            cpf = request.form['cpf']
            email = request.form['email']

            if acao_id:
                acao = Acao.query.get(int(acao_id))
                if acao:
                    acao.subfuncao = subfuncao
                    acao.acao_paoe = acao_paoe
                    acao.responsavel = responsavel
                    acao.cpf = cpf
                    acao.email = email
                    acao.alterado_em = datetime.now()
            else:
                nova_acao = Acao(
                    programa_id=programa_id,
                    subfuncao=subfuncao,
                    acao_paoe=acao_paoe,
                    responsavel=responsavel,
                    cpf=cpf,
                    email=email,
                    ativo=True
                )
                db.session.add(nova_acao)

            db.session.commit()
            return redirect(url_for('acoes_por_programa', programa_id=programa_id))
        @app.route('/excluir_acao/<int:id>', methods=['POST'])
        def excluir_acao(id):
            acao = Acao.query.get(id)
            if acao:
                acao.ativo = False
                acao.excluido_em = datetime.now()
                db.session.commit()
            return redirect(url_for('acoes_por_programa', programa_id=acao.programa_id))

        # === ETAPA 5: Visualizar Produtos da Ação ===
        @app.route('/produtos_acao/<int:programa_id>/<int:acao_id>')
        def cadastrar_produto_acao(programa_id, acao_id):
            acao = Acao.query.get_or_404(acao_id)
            programa = Programa.query.get_or_404(acao.programa_id)
            produtos = ProdutoAcao.query.filter_by(acao_id=acao_id, ativo=True).all()
            return render_template(
                'cadastrar_produto_acao.html',
                programa=programa,
                acao=acao,
                produtos=produtos
            )

        # === ETAPA 6: Inserir ou Editar Produto da Ação ===
        @app.route('/inserir_produto_acao', methods=['POST'])
        def inserir_produto_acao():
            produto_id = request.form.get('produto_id')
            nome = request.form.get('nome')
            acao_id = request.form.get('acao_id')
            un_medida = request.form.get('un_medida')
            quantidade = request.form.get('quantidade')

            if not nome or not acao_id or not un_medida or not quantidade:
                return "Dados incompletos", 400

            if produto_id:
                produto = ProdutoAcao.query.get(int(produto_id))
                if produto:
                    produto.nome = nome
                    produto.un_medida = un_medida
                    produto.quantidade = float(quantidade)
                    produto.alterado_em = datetime.now()
            else:
                novo_produto = ProdutoAcao(
                    nome=nome,
                    acao_id=acao_id,
                    un_medida=un_medida,
                    quantidade=float(quantidade),
                    ativo=True
                )
                db.session.add(novo_produto)

            db.session.commit()

            acao = Acao.query.get_or_404(int(acao_id))
            return redirect(url_for('cadastrar_produto_acao', programa_id=acao.programa_id, acao_id=acao_id))


        # === EXCLUIR Produto da Ação (Soft Delete) ===
        @app.route('/excluir_produto_acao/<int:id>', methods=['POST'])
        def excluir_produto_acao(id):
            produto = ProdutoAcao.query.get_or_404(id)
            produto.ativo = False
            produto.excluido_em = datetime.now()
            db.session.commit()

            # Obter programa_id para redirecionamento
            acao = Acao.query.get_or_404(produto.acao_id)
            return redirect(url_for('cadastrar_produto_acao', programa_id=acao.programa_id, acao_id=acao.id))

        # === ETAPA 7: Visualização da Subação/Entrega ===
        @app.route('/subacoes_entrega/<int:programa_id>/<int:acao_id>/<int:produto_id>')
        def subacoes_entrega(programa_id, acao_id, produto_id):
            try:
                programa = Programa.query.get_or_404(programa_id)
                acao = Acao.query.get_or_404(acao_id)
                produto = ProdutoAcao.query.get_or_404(produto_id)
                registros = SubacaoEntrega.query.filter_by(produto_id=produto_id, ativo=True).all()
                subacao_ids = [r.id for r in registros]
                municipios = MunicipioEntrega.query.filter(
                    MunicipioEntrega.subacao_entrega_id.in_(subacao_ids)
                ).all()
                mensagem_popup = session.pop('mensagem_popup', None)
                return render_template("subacao_entrega.html",
                                    programa=programa,
                                    acao=acao,
                                    produto=produto,
                                    registros=registros,
                                    municipios=municipios,
                                    mensagem_popup=mensagem_popup)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"<h3>❌ Erro no carregamento:</h3><pre>{e}</pre>", 500


        @app.route('/inserir_subacao_entrega', methods=['POST'])
        def inserir_subacao_entrega():
            try:
                subacao_id = request.form.get('subacao_id')
                produto_id = request.form.get('produto_id')
                quantidade_str = request.form.get("quantidade", "").replace(",", ".")
                try:
                    quantidade = float(quantidade_str) if quantidade_str else 0.0
                except ValueError:
                    return jsonify(sucesso=False, mensagem="Quantidade inválida."), 400

                regiao = request.form.get('regiao')
                subfuncao_ug = request.form.get('subfuncao_ug')
                adj = request.form.get('adj')
                macropolitica = request.form.get('macropolitica')
                pilar = request.form.get('pilar')
                eixo = request.form.get('eixo')
                politica_decreto = request.form.get('politica_decreto')
                publico_ods = request.form.get('publico_ods')
                subacao_entrega_raw = request.form.get('subacao_entrega')
                subacao_entrega_completo = f"* {regiao} * {subfuncao_ug} * {adj} * {macropolitica} * {pilar} * {eixo} * {politica_decreto} * {publico_ods} * {subacao_entrega_raw}"

                dados = {
                    'subacao_entrega': subacao_entrega_completo,
                    'produto_subacao': request.form.get('produto_subacao'),
                    'unidade_gestora': request.form.get('unidade_gestora'),
                    'unidade_setorial': request.form.get('unidade_setorial'),
                    'unidade_medida': request.form.get('unidade_medida'),
                    'quantidade': quantidade,
                    'detalhamento': request.form.get('detalhamento'),
                    'responsavel': request.form.get('responsavel'),
                    'cpf': request.form.get('cpf'),
                    'email': request.form.get('email'),
                    'regiao': regiao,
                    'subfuncao_ug': subfuncao_ug,
                    'adj': adj,
                    'macropolitica': macropolitica,
                    'pilar': pilar,
                    'eixo': eixo,
                    'politica_decreto': politica_decreto,
                    'publico_ods': publico_ods,
                }

                municipios_json = request.form.get('municipios_json')
                if not municipios_json or municipios_json == "[]":
                    return jsonify(sucesso=False, mensagem="É obrigatório cadastrar ao menos um município antes de salvar a subação."), 400

                if subacao_id:
                    registro_antigo = SubacaoEntrega.query.get_or_404(int(subacao_id))
                    registro_antigo.ativo = False
                    registro_antigo.alterado_em = datetime.now()
                    MunicipioEntrega.query.filter_by(subacao_entrega_id=registro_antigo.id, ativo=True).update({
                        'ativo': False,
                        'alterado_em': datetime.now()
                    })
                else:
                    subacao_existente = SubacaoEntrega.query.filter_by(
                        produto_id=produto_id,
                        regiao=regiao,
                        subfuncao_ug=subfuncao_ug,
                        adj=adj,
                        macropolitica=macropolitica,
                        pilar=pilar,
                        eixo=eixo,
                        politica_decreto=politica_decreto,
                        publico_ods=publico_ods,
                        subacao_entrega=subacao_entrega_completo,
                        ativo=True
                    ).first()
                    if subacao_existente:
                        return jsonify(sucesso=False, mensagem="❌ Já existe uma subação com a mesma chave de planejamento e nome."), 409

                registro = SubacaoEntrega(**dados, produto_id=produto_id, ativo=True)
                db.session.add(registro)
                db.session.commit()

                import json
                municipios = json.loads(municipios_json)
                for m in municipios:
                    novo_municipio = MunicipioEntrega(
                        subacao_entrega_id=registro.id,
                        codigo_municipio=m.get('codigo'),
                        nome_municipio=m.get('nome'),
                        un_medida=m.get('un_medida'),
                        quantidade=float(str(m.get('quantidade')).replace(",", ".")),
                        ativo=True,
                        alterado_em=datetime.now()
                    )
                    db.session.add(novo_municipio)
                db.session.commit()

                return jsonify(sucesso=True)
            except Exception as e:
                db.session.rollback()
                return jsonify(sucesso=False, mensagem=f"Erro ao salvar a Subação: {str(e)}"), 500
            
        # === ALTERAR Subação/Entrega ===
        @app.route('/subacao_entrega_json/<int:id>')
        def subacao_entrega_json(id):
            try:
                registro = SubacaoEntrega.query.get_or_404(id)

                # Busca os municípios vinculados à subação
                municipios = MunicipioEntrega.query.filter_by(subacao_entrega_id=id).all()
                lista_municipios = [
                    {
                        "id": m.id,
                        "codigo_municipio": m.codigo_municipio,
                        "nome_municipio": m.nome_municipio,
                        "unidade_medida": m.un_medida,
                        "quantidade": str(m.quantidade).replace('.', ',')
                    }
                    for m in municipios
                ]

                dados = {
                    "id": registro.id,
                    "produto_subacao": registro.produto_subacao,
                    "unidade_gestora": registro.unidade_gestora,
                    "unidade_setorial": registro.unidade_setorial,
                    "un_medida": registro.unidade_medida,
                    "quantidade": str(registro.quantidade).replace('.', ','),
                    "detalhamento": registro.detalhamento,
                    "responsavel": registro.responsavel,
                    "cpf": registro.cpf,
                    "email": registro.email,
                    "regiao": registro.regiao,
                    "subfuncao_ug": registro.subfuncao_ug,
                    "adj": registro.adj,
                    "macropolitica": registro.macropolitica,
                    "pilar": registro.pilar,
                    "eixo": registro.eixo,
                    "politica_decreto": registro.politica_decreto,
                    "publico_ods": registro.publico_ods,
                    "subacao_entrega_raw": registro.subacao_entrega.split("*").pop().strip(),
                    "municipios": lista_municipios
                }

                return jsonify(dados)

            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({"erro": f"Erro ao carregar subação: {str(e)}"}), 500

        # === EXCLUIR Subação/Entrega ===
        @app.route('/excluir_subacao_entrega/<int:id>', methods=['POST'])
        def excluir_subacao_entrega(id):
            try:
                # Desativa a subação
                registro = SubacaoEntrega.query.get_or_404(id)
                registro.ativo = False
                registro.excluido_em = datetime.now()

                # Desativa todos os municípios vinculados à subação
                MunicipioEntrega.query.filter_by(subacao_entrega_id=registro.id, ativo=True).update({
                    'ativo': False,
                    'excluido_em': datetime.now()
                })

                db.session.commit()

                # Redireciona de volta para a visualização
                produto = ProdutoAcao.query.get_or_404(registro.produto_id)
                return redirect(url_for('subacoes_entrega',
                                        programa_id=produto.acao.programa.id,
                                        acao_id=produto.acao.id,
                                        produto_id=produto.id))
            except Exception as e:
                db.session.rollback()
                return f"<h3>❌ Erro ao excluir subação:</h3><pre>{str(e)}</pre>", 500
                    

# Interface WSGI para IIS
# Interface WSGI para IIS
application = app

# Apenas para rodar localmente
if __name__ == '__main__':
    app.run(debug=True)

