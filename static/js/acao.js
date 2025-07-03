function abrirFormularioAcao(alterando = false) {
    const form = document.getElementById("formularioAcao");
    if (!form) return;

    form.style.display = "block";
    const botao = document.getElementById("btnCadastrarAcao");
    botao.innerText = alterando ? "Salvar Alterações" : "Cadastrar";

    const formElement = form.querySelector("form");
    if (formElement) formElement.reset();

    if (alterando) {
        const selecionado = document.querySelector('input[name="acaoSelecionada"]:checked');
        if (!selecionado) {
            alert("Selecione uma ação para alterar.");
            fecharFormularioAcao();
            return;
        }

        const row = selecionado.closest("tr");
        const subfuncaoTexto = row.children[1].innerText.trim();
        const acaoTexto = row.children[2].innerText.trim();
        const responsavel = row.children[3].innerText.trim();
        const cpf = row.children[4].innerText.trim();
        const email = row.children[5].innerText.trim();

        const selectSubfuncao = document.getElementById("selectSubfuncao");
        const selectAcao = document.getElementById("acao_paoe");

        // Carrega subfunções e depois ações
        carregarSubfuncoesPorPrograma(nomeProgramaAtual, selectSubfuncao, () => {
            selectSubfuncao.value = subfuncaoTexto;
            carregarAcoesFiltradas(nomeProgramaAtual, subfuncaoTexto, selectAcao, acaoTexto);
        });

        document.getElementById("respAcao").value = responsavel;
        document.getElementById("cpfAcao").value = cpf;
        document.getElementById("emailAcao").value = email;
        document.getElementById("acao_id").value = selecionado.value;
    } else {
        document.getElementById("acao_id").value = "";
    }
}

function fecharFormularioAcao() {
    const form = document.getElementById("formularioAcao");
    if (!form) return;

    form.style.display = "none";
    const formElement = form.querySelector("form");
    if (formElement) formElement.reset();

    document.getElementById("acao_id").value = "";
    document.getElementById("btnCadastrarAcao").innerText = "Cadastrar";

    const selecionado = document.querySelector('input[name="acaoSelecionada"]:checked');
    if (selecionado) selecionado.checked = false;
}

function validarAcao() {
    const subfuncao = document.getElementById("selectSubfuncao")?.value;
    const acaoPaoe = document.getElementById("acao_paoe")?.value;
    const responsavel = document.getElementById("respAcao")?.value.trim();
    const cpf = document.getElementById("cpfAcao")?.value.trim();
    const email = document.getElementById("emailAcao")?.value.trim();

    if (!subfuncao || !acaoPaoe || !responsavel || !cpf || !email) {
        alert("Todos os campos são obrigatórios.");
        return;
    }

    if (!validarCPF(cpf)) {
        alert("CPF inválido.");
        return;
    }

    if (!validarEmail(email)) {
        alert("E-mail inválido.");
        return;
    }

    document.querySelector("#formularioAcao form").submit();
}

function excluirAcao() {
    const selecionado = document.querySelector('input[name="acaoSelecionada"]:checked');
    if (!selecionado) {
        alert("Selecione uma ação para excluir.");
        return;
    }

    if (confirm("Deseja realmente excluir esta ação?")) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/excluir_acao/${selecionado.value}`;
        document.body.appendChild(form);
        form.submit();
    }
}

// === Inicialização DOM ===
document.addEventListener('DOMContentLoaded', () => {
    const cpfInput = document.getElementById("cpfAcao");
    if (cpfInput) {
        cpfInput.addEventListener("input", () => {
            cpfInput.value = formatarCPF(cpfInput.value);
        });
    }

    const selectSubfuncao = document.getElementById("selectSubfuncao");
    const selectAcao = document.getElementById("acao_paoe");

    if (typeof nomeProgramaAtual !== "undefined" && selectSubfuncao) {
        carregarSubfuncoesPorPrograma(nomeProgramaAtual, selectSubfuncao);
    }

    if (selectSubfuncao && selectAcao) {
        selectSubfuncao.addEventListener("change", function () {
            carregarAcoesFiltradas(nomeProgramaAtual, this.value, selectAcao);
        });
    }
});

// === Expor funções no escopo global ===
window.abrirFormularioAcao = abrirFormularioAcao;
window.fecharFormularioAcao = fecharFormularioAcao;
window.validarAcao = validarAcao;
window.excluirPrograma = excluirAcao;

