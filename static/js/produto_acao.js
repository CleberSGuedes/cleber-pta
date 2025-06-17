// === Lista de produtos vinculados às ações ===
const produtosPorAcao = {
    "2900": ["Acesso e permanência desenvolvido", "Avaliação (Avalia MT) desenvolvida", "Bem-estar escolar desenvolvido", "Educação para jovens e adultos (EJA) desenvolvida", "Formação continuada de professores realizada", "Línguas estrangeiras desenvolvidas", "Materiais escolares disponibilizados", "Projetos pedagógicos integrados implantados", "Sistema estruturado de ensino implantado", "Uniformes escolares disponibilizados"],
    "2936": ["Acesso e permanência desenvolvido", "Alfabetização desenvolvida", "Avaliação (Avalia MT) desenvolvida", "Bem-estar escolar desenvolvido", "Educação em tempo integral desenvolvida", "Educação escolar do campo desenvolvida", "Educação escolar indígena desenvolvida", "Educação escolar quilombola desenvolvida", "Educação especial desenvolvida", "Educação para jovens e adultos (EJA) desenvolvida", "Escolas militares desenvolvidas", "Formação continuada de professores realizada", "Línguas estrangeiras desenvolvidas", "Projetos pedagógicos integrados implantados", "Sistema estruturado de ensino implantado"],
    "2957": ["Acesso e permanência desenvolvido", "Alfabetização desenvolvida", "Avaliação (Avalia MT) desenvolvida", "Bem-estar escolar desenvolvido", "Educação especial desenvolvida", "Formação continuada de professores realizada", "Línguas estrangeiras desenvolvidas", "Materiais escolares disponibilizados", "Projetos pedagógicos integrados implantados", "Sistema estruturado de ensino implantado", "Uniformes escolares disponibilizados"],
    "4172": ["Acesso e permanência desenvolvido", "Alfabetização desenvolvida", "Avaliação (Avalia MT) desenvolvida", "Bem-estar escolar desenvolvido", "Educação em tempo integral desenvolvida", "Educação escolar do campo desenvolvida", "Educação escolar indígena desenvolvida", "Educação escolar quilombola desenvolvida", "Escolas militares desenvolvidas", "Formação continuada de professores realizada", "Línguas estrangeiras desenvolvidas", "Materiais escolares disponibilizados", "Projetos pedagógicos integrados implantados", "Remuneração professores e profissionais da educação com recursos do MDE, Art 70 Lei 9394/1996", "Remuneração professores e profissionais da educação, FUNDEB 30%, Arts 26-A, 14.113/20 e 70, 9394/96", "Remuneração professores e profissionais da educação, FUNDEB 70%, Art 26, § 1º, II, Lei 14.113/20", "Sistema estruturado de ensino implantado", "Uniformes escolares disponibilizados"],
    "4174": ["Acesso e permanência desenvolvido", "Avaliação (Avalia MT) desenvolvida", "Bem-estar escolar desenvolvido", "Educação em tempo integral desenvolvida", "Educação escolar do campo desenvolvida", "Educação escolar indígena desenvolvida", "Educação escolar quilombola desenvolvida", "Escolas militares desenvolvidas", "Formação continuada de professores realizada", "Línguas estrangeiras desenvolvidas", "Materiais escolares disponibilizados", "Novo ensino médio e ensino técnico profissionalizante desenvolvido", "Projetos pedagógicos integrados implantados", "Sistema estruturado de ensino implantado", "Uniformes escolares disponibilizados"],
    "2895": ["Alimentação escolar mantida"],
    "2897": ["Alimentação escolar mantida"],
    "2898": ["Alimentação escolar mantida"],
    "2899": ["Alimentação escolar mantida"],
    "2284": ["Conselho mantido"],
    "4173": ["Gestão do patrimônio realizada", "Gestão escolar desenvolvida", "Infraestrutura escolar modernizada", "Tecnologia no ambiente escolar disponibilizada"],
    "4175": ["Gestão do patrimônio realizada", "Gestão escolar desenvolvida", "Infraestrutura escolar modernizada", "Tecnologia no ambiente escolar disponibilizada"],
    "4177": ["Gestão do patrimônio realizada", "Gestão escolar desenvolvida", "Infraestrutura escolar modernizada", "Tecnologia no ambiente escolar disponibilizada"],
    "4178": ["Gestão do patrimônio realizada", "Gestão escolar desenvolvida", "Infraestrutura escolar modernizada", "Tecnologia no ambiente escolar disponibilizada"],
    "4180": ["Gestão do patrimônio realizada", "Gestão escolar desenvolvida", "Gestão estratégica de pessoas implementada", "Gestão integrada desenvolvida", "Infraestrutura escolar modernizada", "Regime de colaboração desenvolvido", "Valorização profissional desenvolvida"],
    "4524": ["Infraestrutura escolar modernizada", "Regime de colaboração desenvolvido"],
    "4525": ["Infraestrutura escolar modernizada", "Regime de colaboração desenvolvido"],
    "4179": ["Transporte escolar mantido"],
    "4181": ["Transporte escolar mantido"],
    "4182": ["Transporte escolar mantido"],
    "2009": ["Produto exclusivo para ação padronizada"],
    "2010": ["Produto exclusivo para ação padronizada"],
    "2014": ["Produto exclusivo para ação padronizada"],
    "4491": ["Produto exclusivo para ação padronizada"],
    "8002": ["Produto exclusivo para ação padronizada"],
    "8026": ["Produto exclusivo para ação padronizada"],
    "8040": ["Produto exclusivo para ação padronizada"],
    "8003": ["Produto exclusivo para ação padronizada"]
};

// === Preenche a lista de produtos com base na ação selecionada ===
function carregarProdutosPorAcao(acaoPaoeCodigo) {
    const select = document.getElementById("produto_acao");
    select.innerHTML = '<option value="">Selecione um produto</option>';

    const codigo = acaoPaoeCodigo?.split(" - ")[0];
    const produtos = produtosPorAcao[codigo] || [];

    produtos.forEach(produto => {
        const opt = document.createElement("option");
        opt.value = produto;
        opt.textContent = produto;
        select.appendChild(opt);
    });
}

// === Abrir formulário de produto ===
function abrirFormularioProduto(alterando = false) {
    const form = document.getElementById("formularioProduto");
    if (!form) return;

    form.style.display = "block";

    const select = document.getElementById("produto_acao");
    const btn = document.getElementById("btnCadastrarProduto");
    const produtoId = document.getElementById("produto_id");

    const unMedidaSelect = document.getElementById("un_medida");
    const quantidadeInput = document.getElementById("quantidade");

    btn.innerText = "Cadastrar";
    produtoId.value = "";
    select.selectedIndex = 0;
    unMedidaSelect.selectedIndex = 0;
    quantidadeInput.value = "";

    if (alterando) {
        const selecionado = document.querySelector('input[name="produtoSelecionado"]:checked');
        if (!selecionado) {
            alert("Selecione um produto para alterar.");
            fecharFormularioProduto();
            return;
        }

        const row = selecionado.closest('tr');
        const nome = row.children[1].innerText.trim();
        const unMedida = row.children[2].innerText.trim();
        const quantidade = row.children[3].innerText.trim();

        Array.from(select.options).forEach(opt => {
            if (opt.textContent === nome) opt.selected = true;
        });

        Array.from(unMedidaSelect.options).forEach(opt => {
            if (opt.textContent === unMedida) opt.selected = true;
        });

        quantidadeInput.value = quantidade;

        produtoId.value = selecionado.value;
        btn.innerText = "Salvar Alterações";
    }
}

// === Fechar formulário ===
function fecharFormularioProduto() {
    const form = document.getElementById("formularioProduto");
    if (!form) return;

    form.style.display = "none";
    form.querySelector("form").reset();
    document.getElementById("produto_id").value = "";
    document.getElementById("btnCadastrarProduto").innerText = "Cadastrar";

    // 🧹 Desmarca o radio selecionado ao voltar
    const selecionado = document.querySelector('input[name="produtoSelecionado"]:checked');
    if (selecionado) selecionado.checked = false;
}

// === Validar e submeter ===
function validarProduto() {
    const nomeSelect = document.getElementById("produto_acao");
    const unMedidaSelect = document.getElementById("un_medida");
    const quantidadeInput = document.getElementById("quantidade");

    const nome = nomeSelect?.value;
    const unMedida = unMedidaSelect?.value;
    const quantidade = parseFloat(quantidadeInput?.value);

    // Validações
    if (!nome) {
        alert("Selecione um produto da ação.");
        nomeSelect.focus();
        return;
    }

    if (!unMedida) {
        alert("Selecione a unidade de medida.");
        unMedidaSelect.focus();
        return;
    }

    if (isNaN(quantidade) || quantidade <= 0) {
        alert("Informe uma quantidade válida (número maior que 0).");
        quantidadeInput.focus();
        return;
    }

    // ✅ Nova Regra: se for Percentual, quantidade não pode ultrapassar 100
    if (unMedida === "Percentual" && quantidade > 100) {
        alert("Para unidade Percentual, a quantidade não pode ser maior que 100.");
        quantidadeInput.focus();
        return;
    }

    // Se tudo estiver certo, envia o formulário
    document.getElementById("formProdutoAcao").submit();
}

// === Excluir produto ===
function excluirProduto() {
    const selecionado = document.querySelector('input[name="produtoSelecionado"]:checked');
    if (!selecionado) {
        alert("Selecione um produto para excluir.");
        return;
    }

    if (confirm("Deseja realmente excluir este produto da ação?")) {
        const form = document.createElement("form");
        form.method = "POST";
        form.action = `/excluir_produto_acao/${selecionado.value}`;
        document.body.appendChild(form);
        form.submit();
    }
}

// === Inicialização DOM ===
document.addEventListener("DOMContentLoaded", () => {
    const acaoPaoe = document.getElementById("acao_paoe_info");
    if (acaoPaoe) carregarProdutosPorAcao(acaoPaoe.value);

    const cpfInput = document.getElementById("cpfProduto");
    if (cpfInput) {
        cpfInput.addEventListener("input", () => {
            cpfInput.value = formatarCPF(cpfInput.value);
        });
    }

    // 🧹 Desmarcar seleção ao recarregar a página
    const selecionado = document.querySelector('input[name="produtoSelecionado"]:checked');
    if (selecionado) selecionado.checked = false;
});

// === Expor funções globais ===
window.abrirFormularioProduto = abrirFormularioProduto;
window.fecharFormularioProduto = fecharFormularioProduto;
window.validarProduto = validarProduto;
window.excluirProduto = excluirProduto;
