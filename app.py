from flask import Flask, app, flash, jsonify, render_template, request, redirect, url_for
from config import Config
from extensions import db
from datetime import datetime, timedelta
import io
import uuid
import pandas as pd
from flask import send_file
from models import Programa, Acao
from models import ProdutoAcao  # certifique-se de importar no topo com os outros modelos
from models import SubacaoEntrega  # certifique-se de importar no topo com os outros modelos
from models import MunicipioEntrega
from models import Etapa
from models import MemoriaCalculo
from flask import session

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
usuarios_online = {}

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

            if not programa:
                flash('Programa não encontrado.', 'danger')
                return redirect(url_for('cadastrar_pta'))

            # Verificar se há ações ativas vinculadas a este programa
            acoes_vinculadas = Acao.query.filter_by(programa_id=id, ativo=True).first()
            if acoes_vinculadas:
                flash('Não é possível excluir o programa. Existem ações ativas vinculadas a ele.', 'warning')
                return redirect(url_for('cadastrar_pta'))

            # Exclusão lógica do programa
            programa.ativo = False
            programa.excluido_em = datetime.now()
            db.session.commit()
            
            flash('Programa excluído com sucesso.', 'success')
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

            if not acao:
                flash('Ação não encontrada.', 'danger')
                return redirect(url_for('cadastrar_pta'))

            # Verifica se existem produtos vinculados e ativos
            produtos_vinculados = ProdutoAcao.query.filter_by(acao_id=id, ativo=True).first()
            if produtos_vinculados:
                flash('Não é possível excluir a ação. Existem produtos ativos vinculados a ela.', 'warning')
                return redirect(url_for('acoes_por_programa', programa_id=acao.programa_id))

            # Exclusão lógica
            acao.ativo = False
            acao.excluido_em = datetime.now()
            db.session.commit()

            flash('Ação excluída com sucesso.', 'success')
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

            # Verificar se há subações vinculadas ativas
            subacoes = SubacaoEntrega.query.filter_by(produto_id=id, ativo=True).first()
            if subacoes:
                acao = Acao.query.get_or_404(produto.acao_id)
                flash('Não é possível excluir o produto. Existem subações/entregas ativas vinculadas a ele.', 'warning')
                return redirect(url_for('cadastrar_produto_acao', programa_id=acao.programa_id, acao_id=acao.id))

            # Exclusão lógica
            produto.ativo = False
            produto.excluido_em = datetime.now()
            db.session.commit()

            acao = Acao.query.get_or_404(produto.acao_id)
            flash('Produto da ação excluído com sucesso.', 'success')
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
                        codigo_municipio=m.get('codigo') or m.get('codigo_municipio'),
                        nome_municipio=m.get('nome') or m.get('nome_municipio'),
                        un_medida=m.get('un_medida') or m.get('unidade_medida'),
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

                # ✅ CORRIGIDO: nomes dos campos compatíveis com o JS
                lista_municipios = [
                    {
                        "id": m.id,
                        "codigo": m.codigo_municipio,
                        "nome": m.nome_municipio,
                        "un_medida": m.un_medida,
                        "quantidade": str(m.quantidade).replace('.', ',')
                    }
                    for m in municipios
                ]

                # Dados do produto → ação → programa
                produto = ProdutoAcao.query.get_or_404(registro.produto_id)
                acao = produto.acao
                programa = acao.programa

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

                    # ✅ Aqui estão os municípios com campos já ajustados
                    "municipios": lista_municipios,

                    # 🔁 DADOS DE PLANEJAMENTO corrigidos com base no seu models.py
                    "programa": f"{programa.id} - {programa.nome}",
                    "subfuncao": acao.subfuncao,  # já vem no formato "367 - EDUCAÇÃO ESPECIAL"
                    "paoe": acao.acao_paoe        # já vem no formato "2957 - Desenvolvimento..."
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
            
        # Pagina Etapa 
        @app.route('/etapas/<int:programa_id>/<int:acao_id>/<int:produto_id>/<int:subacao_id>')
        def etapas(programa_id, acao_id, produto_id, subacao_id):
            try:
                programa = Programa.query.get_or_404(programa_id)
                acao = Acao.query.get_or_404(acao_id)
                produto = ProdutoAcao.query.get_or_404(produto_id)
                subacao = SubacaoEntrega.query.get_or_404(subacao_id)
                etapas = Etapa.query.filter_by(subacao_entrega_id=subacao.id, ativo=True).all()

                # Capturar e limpar mensagem de popup
                mensagem = session.pop('mensagem_popup', None)

                return render_template(
                    "etapa.html",
                    programa=programa,
                    acao=acao,
                    produto=produto,
                    subacao_entrega=subacao,  # <- nome compatível com o template
                    etapas=etapas,
                    mensagem_popup=mensagem
                )

            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"<h3>❌ Erro ao carregar a tela de Etapas:</h3><pre>{e}</pre>", 500
    
        @app.route('/inserir_etapa', methods=['POST'])
        def inserir_etapa():
            try:
                etapa_id = request.form.get("etapa_id")
                subacao_id = request.form.get("subacao_entrega_id")
                subacao = SubacaoEntrega.query.get_or_404(subacao_id)

                if etapa_id:
                    etapa = Etapa.query.get_or_404(etapa_id)
                else:
                    etapa = Etapa(subacao_entrega_id=subacao.id)

                etapa.etapa_nome = request.form.get("etapa_nome")
                etapa.data_inicio = request.form.get("data_inicio")
                etapa.data_fim = request.form.get("data_fim")
                etapa.responsavel = request.form.get("responsavel")
                etapa.cpf = request.form.get("cpf")
                etapa.email = request.form.get("email")
                etapa.ativo = True
                etapa.alterado_em = datetime.now()

                db.session.add(etapa)
                db.session.commit()

                session['mensagem_popup'] = "Etapa salva com sucesso."

                # Redirecionar para evitar reenvio do formulário
                produto = ProdutoAcao.query.get_or_404(subacao.produto_id)
                acao = Acao.query.get_or_404(produto.acao_id)
                programa = Programa.query.get_or_404(acao.programa_id)

                return redirect(url_for('etapas',
                                        programa_id=programa.id,
                                        acao_id=acao.id,
                                        produto_id=produto.id,
                                        subacao_id=subacao.id))
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"<h3>❌ Erro ao salvar a etapa:</h3><pre>{e}</pre>", 500
    
        @app.route('/excluir_etapa/<int:id>', methods=['POST'])
        def excluir_etapa(id):
            etapa = Etapa.query.get_or_404(id)
            etapa.ativo = False
            etapa.excluido_em = datetime.utcnow()
            db.session.commit()

            subacao = SubacaoEntrega.query.get_or_404(etapa.subacao_entrega_id)
            produto = ProdutoAcao.query.get_or_404(subacao.produto_id)
            acao = Acao.query.get_or_404(produto.acao_id)
            programa = Programa.query.get_or_404(acao.programa_id)

            session['mensagem_popup'] = "✅ Etapa excluída com sucesso."

            return redirect(url_for(
                'etapas',
                programa_id=programa.id,
                acao_id=acao.id,
                produto_id=produto.id,
                subacao_id=subacao.id
            ))

        # Pagina Memória de Cálculo    
        @app.route("/memoria_calculo/<int:programa_id>/<int:acao_id>/<int:produto_id>/<int:subacao_id>/<int:etapa_id>")
        def memoria_calculo(programa_id, acao_id, produto_id, subacao_id, etapa_id):
            try:
                programa = Programa.query.get(programa_id)
                acao = Acao.query.get(acao_id)
                produto = ProdutoAcao.query.get(produto_id)
                subacao_entrega = SubacaoEntrega.query.get(subacao_id)
                etapa = Etapa.query.get(etapa_id)

                if not all([programa, acao, produto, subacao_entrega, etapa]):
                    raise Exception("Algum dos objetos está ausente no banco de dados.")

                memorias = MemoriaCalculo.query.filter_by(etapa_id=etapa_id, ativo=True).all()

                # Pega e remove a mensagem da sessão, se houver
                mensagem = session.pop('mensagem_popup', None)

                return render_template(
                    "memoria_calculo.html",
                    programa=programa,
                    acao=acao,
                    produto=produto,
                    subacao_entrega=subacao_entrega,
                    etapa=etapa,
                    memorias=memorias,
                    mensagem_popup=mensagem
                )

            except Exception as e:
                return f"<h3>❌ Erro ao carregar a Memória de Cálculo:</h3><pre>{str(e)}</pre>"

        @app.route("/inserir_memoria", methods=["POST"])
        def inserir_memoria():
            memoria_id = request.form.get("memoria_id")
            etapa_id = request.form.get("etapa_id")

            # Função robusta para converter string em float
            def parse_float(valor_str):
                if not valor_str:
                    return 0.0
                valor_str = valor_str.strip()
                if ',' in valor_str and '.' in valor_str:
                    # Ex: 1.234,56 → remover milhar e trocar decimal
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                elif ',' in valor_str:
                    # Ex: 1234,56 → troca somente decimal
                    valor_str = valor_str.replace(',', '.')
                # Se já estiver com ponto decimal padrão, mantém
                try:
                    return float(valor_str)
                except ValueError:
                    return 0.0

            dados = {
                'itens_despesa': request.form.get("itens_despesa"),
                'unidade_medida': request.form.get("unidade_medida"),
                'quantidade': parse_float(request.form.get("quantidade_real")),
                'valor_unitario': parse_float(request.form.get("valor_unitario_real")),
                'valor_total': parse_float(request.form.get("valor_total_real")),
                'categoria_economica': request.form.get("categoria_economica"),
                'grupo_despesa': request.form.get("grupo_despesa"),
                'modalidade': request.form.get("modalidade"),
                'elemento_despesa': request.form.get("elemento_despesa"),
                'subelemento': request.form.get("subelemento"),
                'fonte_recursos': request.form.get("fonte_recursos"),
                'identificador_uso': request.form.get("identificador_uso"),
                'legislacao': request.form.get("legislacao"),
            }

            if memoria_id:
                memoria = MemoriaCalculo.query.get(memoria_id)
                for campo, valor in dados.items():
                    setattr(memoria, campo, valor)
                memoria.alterado_em = datetime.utcnow()
            else:
                memoria = MemoriaCalculo(etapa_id=etapa_id, **dados)
                db.session.add(memoria)

            db.session.commit()
            session['mensagem_popup'] = "Memória de Cálculo salva com sucesso."

            # Redirecionamento com dados relacionados
            etapa = Etapa.query.get(etapa_id)
            subacao = SubacaoEntrega.query.get(etapa.subacao_entrega_id)
            produto = ProdutoAcao.query.get(subacao.produto_id)
            acao = Acao.query.get(produto.acao_id)
            programa = Programa.query.get(acao.programa_id)

            return redirect(url_for("memoria_calculo",
                programa_id=programa.id,
                acao_id=acao.id,
                produto_id=produto.id,
                subacao_id=subacao.id,
                etapa_id=etapa.id
            ))


        @app.route("/excluir_memoria/<int:id>", methods=["POST"])
        def excluir_memoria(id):
            memoria = MemoriaCalculo.query.get_or_404(id)
            memoria.ativo = False
            memoria.excluido_em = datetime.utcnow()
            db.session.commit()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return '', 204  # Sem conteúdo, mas sem erro

            # fallback padrão, se alguém acessar via formulário normal
            etapa = Etapa.query.get(memoria.etapa_id)
            subacao = etapa.subacao_entrega
            produto = subacao.produto_acao
            acao = produto.acao
            programa = acao.programa

            return redirect(url_for("memoria_calculo",
                programa_id=programa.id,
                acao_id=acao.id,
                produto_id=produto.id,
                subacao_id=subacao.id,
                etapa_id=etapa.id
            ))
        
        # Pagina Visualizar PTA
        @app.route('/visualizar')
        def visualizar_pta():
            dados = (
                db.session.query(
                    Programa.nome.label("programa_nome"),
                    Programa.funcao,
                    Programa.responsavel.label("programa_responsavel"),
                    Programa.cpf.label("programa_cpf"),
                    Programa.email.label("programa_email"),

                    Acao.subfuncao,
                    Acao.acao_paoe,
                    Acao.responsavel.label("acao_responsavel"),
                    Acao.cpf.label("acao_cpf"),
                    Acao.email.label("acao_email"),

                    ProdutoAcao.nome.label("produto_nome"),
                    ProdutoAcao.un_medida,
                    ProdutoAcao.quantidade.label("produto_quantidade"),

                    SubacaoEntrega.subacao_entrega,
                    SubacaoEntrega.produto_subacao,
                    SubacaoEntrega.unidade_gestora,
                    SubacaoEntrega.unidade_setorial,
                    SubacaoEntrega.unidade_medida,
                    SubacaoEntrega.quantidade.label("subacao_quantidade"),
                    SubacaoEntrega.detalhamento,
                    SubacaoEntrega.responsavel.label("subacao_responsavel"),
                    SubacaoEntrega.cpf.label("subacao_cpf"),
                    SubacaoEntrega.email.label("subacao_email"),
                    SubacaoEntrega.regiao,
                    SubacaoEntrega.subfuncao_ug,
                    SubacaoEntrega.adj,
                    SubacaoEntrega.macropolitica,
                    SubacaoEntrega.pilar,
                    SubacaoEntrega.eixo,
                    SubacaoEntrega.politica_decreto,
                    SubacaoEntrega.publico_ods,

                    MunicipioEntrega.codigo_municipio,
                    MunicipioEntrega.nome_municipio,
                    MunicipioEntrega.un_medida.label("municipio_un"),
                    MunicipioEntrega.quantidade.label("municipio_quantidade"),

                    Etapa.etapa_nome,
                    Etapa.data_inicio,
                    Etapa.data_fim,
                    Etapa.responsavel.label("etapa_responsavel"),
                    Etapa.cpf.label("etapa_cpf"),
                    Etapa.email.label("etapa_email"),

                    MemoriaCalculo.itens_despesa,
                    MemoriaCalculo.unidade_medida,
                    MemoriaCalculo.quantidade.label("memoria_quantidade"),
                    MemoriaCalculo.valor_unitario,
                    MemoriaCalculo.valor_total,
                    MemoriaCalculo.categoria_economica,
                    MemoriaCalculo.grupo_despesa,
                    MemoriaCalculo.modalidade,
                    MemoriaCalculo.elemento_despesa,
                    MemoriaCalculo.subelemento,
                    MemoriaCalculo.fonte_recursos,
                    MemoriaCalculo.identificador_uso,
                    MemoriaCalculo.legislacao,
                )
                .join(Acao, Acao.programa_id == Programa.id)
                .join(ProdutoAcao, ProdutoAcao.acao_id == Acao.id)
                .join(SubacaoEntrega, SubacaoEntrega.produto_id == ProdutoAcao.id)
                .outerjoin(MunicipioEntrega, MunicipioEntrega.subacao_entrega_id == SubacaoEntrega.id)
                .outerjoin(Etapa, Etapa.subacao_entrega_id == SubacaoEntrega.id)
                .outerjoin(MemoriaCalculo, MemoriaCalculo.etapa_id == Etapa.id)
                .filter(
                    Programa.ativo == True,
                    Acao.ativo == True,
                    ProdutoAcao.ativo == True,
                    SubacaoEntrega.ativo == True,
                    (MunicipioEntrega.ativo == True) | (MunicipioEntrega.ativo == None),
                    (Etapa.ativo == True) | (Etapa.ativo == None),
                    (MemoriaCalculo.ativo == True) | (MemoriaCalculo.ativo == None)
                )
                .all()
            )

            return render_template("visualizar_pta.html", dados=dados)

        @app.route('/baixar_excel')
        def baixar_excel():
            dados = (
                db.session.query(
                    Programa.nome.label("Programa"),
                    Programa.funcao.label("Função"),
                    Programa.responsavel.label("Responsável Programa"),
                    Programa.cpf.label("CPF Programa"),
                    Programa.email.label("E-mail Programa"),

                    Acao.subfuncao.label("Subfunção"),
                    Acao.acao_paoe.label("Ação PAOE"),
                    Acao.responsavel.label("Responsável Ação"),
                    Acao.cpf.label("CPF Ação"),
                    Acao.email.label("E-mail Ação"),

                    ProdutoAcao.nome.label("Produto da Ação"),
                    ProdutoAcao.un_medida.label("Un. Medida Produto"),
                    ProdutoAcao.quantidade.label("Qtd. Produto"),

                    SubacaoEntrega.subacao_entrega.label("Subação"),
                    SubacaoEntrega.produto_subacao.label("Produto Subação"),
                    SubacaoEntrega.unidade_gestora.label("UG"),
                    SubacaoEntrega.unidade_setorial.label("US"),
                    SubacaoEntrega.unidade_medida.label("Un. Medida Sub."),
                    SubacaoEntrega.quantidade.label("Qtd. Subação"),
                    SubacaoEntrega.detalhamento.label("Detalhamento"),
                    SubacaoEntrega.responsavel.label("Responsável Subação"),
                    SubacaoEntrega.cpf.label("CPF Subação"),
                    SubacaoEntrega.email.label("E-mail Subação"),
                    SubacaoEntrega.regiao.label("Região"),
                    SubacaoEntrega.subfuncao_ug.label("Subfunção UG"),
                    SubacaoEntrega.adj.label("ADJ"),
                    SubacaoEntrega.macropolitica.label("Macropolítica"),
                    SubacaoEntrega.pilar.label("Pilar"),
                    SubacaoEntrega.eixo.label("Eixo"),
                    SubacaoEntrega.politica_decreto.label("Política Decreto"),
                    SubacaoEntrega.publico_ods.label("Público Transversal"),

                    MunicipioEntrega.codigo_municipio.label("Código Município"),
                    MunicipioEntrega.nome_municipio.label("Nome Município"),
                    MunicipioEntrega.un_medida.label("Un. Medida Município"),
                    MunicipioEntrega.quantidade.label("Qtd. Município"),

                    Etapa.etapa_nome.label("Etapa"),
                    Etapa.data_inicio.label("Data Início"),
                    Etapa.data_fim.label("Data Fim"),
                    Etapa.responsavel.label("Responsável Etapa"),
                    Etapa.cpf.label("CPF Etapa"),
                    Etapa.email.label("E-mail Etapa"),

                    MemoriaCalculo.itens_despesa.label("Item Despesa"),
                    MemoriaCalculo.unidade_medida.label("Un. Medida Memória"),
                    MemoriaCalculo.quantidade.label("Qtd. Memória"),
                    MemoriaCalculo.valor_unitario.label("Valor Unitário"),
                    MemoriaCalculo.valor_total.label("Valor Total"),
                    MemoriaCalculo.categoria_economica.label("Categoria Econômica"),
                    MemoriaCalculo.grupo_despesa.label("Grupo de Despesa"),
                    MemoriaCalculo.modalidade.label("Modalidade"),
                    MemoriaCalculo.elemento_despesa.label("Elemento Despesa"),
                    MemoriaCalculo.subelemento.label("Subelemento"),
                    MemoriaCalculo.fonte_recursos.label("Fonte de Recursos"),
                    MemoriaCalculo.identificador_uso.label("ID Uso"),
                    MemoriaCalculo.legislacao.label("Legislação"),
                )
                .join(Acao, Acao.programa_id == Programa.id)
                .join(ProdutoAcao, ProdutoAcao.acao_id == Acao.id)
                .join(SubacaoEntrega, SubacaoEntrega.produto_id == ProdutoAcao.id)
                .outerjoin(MunicipioEntrega, MunicipioEntrega.subacao_entrega_id == SubacaoEntrega.id)
                .outerjoin(Etapa, Etapa.subacao_entrega_id == SubacaoEntrega.id)
                .outerjoin(MemoriaCalculo, MemoriaCalculo.etapa_id == Etapa.id)
                .filter(
                    Programa.ativo == True,
                    Acao.ativo == True,
                    ProdutoAcao.ativo == True,
                    SubacaoEntrega.ativo == True,
                    (MunicipioEntrega.ativo == True) | (MunicipioEntrega.ativo == None),
                    (Etapa.ativo == True) | (Etapa.ativo == None),
                    (MemoriaCalculo.ativo == True) | (MemoriaCalculo.ativo == None)
                )
                .all()
            )

            df = pd.DataFrame([d._asdict() for d in dados])

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='PTA', index=False)
            output.seek(0)

            return send_file(
                output,
                as_attachment=True,
                download_name="pta.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        @app.before_request
        def registrar_usuario_online():
            session.permanent = True
            if 'usuario_id' not in session:
                session['usuario_id'] = str(uuid.uuid4())
            
            usuarios_online[session['usuario_id']] = datetime.now()

            # Remove inativos há mais de 5 minutos
            limite = datetime.now() - timedelta(minutes=5)
            inativos = [uid for uid, t in usuarios_online.items() if t < limite]
            for uid in inativos:
                usuarios_online.pop(uid, None)

        @app.route('/usuarios_online')
        def get_usuarios_online():
            return {'total_online': len(usuarios_online)}

        @app.route('/dashboard_status')
        def dashboard_status():
            # Consulta subações ativas sem etapas
            subacoes_sem_etapa_query = db.session.query(
                SubacaoEntrega.subacao_entrega.label("subacao"),
                ProdutoAcao.nome.label("produto"),
                Acao.acao_paoe.label("acao"),
                Programa.nome.label("programa")
            ).join(ProdutoAcao, ProdutoAcao.id == SubacaoEntrega.produto_id)\
            .join(Acao, Acao.id == ProdutoAcao.acao_id)\
            .join(Programa, Programa.id == Acao.programa_id)\
            .outerjoin(Etapa, (Etapa.subacao_entrega_id == SubacaoEntrega.id) & (Etapa.excluido_em == None) & (Etapa.ativo == True))\
            .filter(
                SubacaoEntrega.excluido_em == None,
                SubacaoEntrega.ativo == True,
                Etapa.id == None
            ).all()

            subacoes_sem_etapa_detalhes = [{
                "subacao": row.subacao,
                "produto": row.produto,
                "acao": row.acao,
                "programa": row.programa
            } for row in subacoes_sem_etapa_query]

            return jsonify({
                "programas": db.session.query(Programa).filter_by(excluido_em=None, ativo=True).count(),
                "acoes": db.session.query(Acao).filter_by(excluido_em=None, ativo=True).count(),
                "produtos": db.session.query(ProdutoAcao).filter_by(excluido_em=None, ativo=True).count(),
                "subacoes": db.session.query(SubacaoEntrega).filter_by(excluido_em=None, ativo=True).count(),
                "etapas": db.session.query(Etapa).filter_by(excluido_em=None, ativo=True).count(),
                "memorias": db.session.query(MemoriaCalculo).filter_by(ativo=True).count(),
                "subacoes_sem_etapa": len(subacoes_sem_etapa_detalhes),
                "subacoes_sem_etapa_detalhes": subacoes_sem_etapa_detalhes
            })



# Interface WSGI para IIS
# Interface WSGI para IIS
application = app

# Apenas para rodar localmente
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)


