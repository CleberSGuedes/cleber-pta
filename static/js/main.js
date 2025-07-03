// === Disponibiliza funções no escopo global manualmente ===
// As funções chamadas aqui já devem estar carregadas nos scripts anteriores

window.mostrarFormulario = mostrarFormulario;
window.fecharFormulario = fecharFormulario;
window.validarFormulario = validarFormulario;
window.excluirPrograma = excluirPrograma;
window.abrirEtapa3 = mostrarEtapa3;

window.abrirFormularioAcao = abrirFormularioAcao;
window.fecharFormularioAcao = fecharFormularioAcao;
window.validarAcao = validarAcao;

// === Inicialização automática ao carregar DOM ===
document.addEventListener('DOMContentLoaded', () => {
    if (typeof fecharFormulario === 'function') fecharFormulario();
    if (typeof fecharFormularioAcao === 'function') fecharFormularioAcao();
});
