// ==========================================================
// CONFIGURAÇÃO — troque pela URL da sua API se ela mudar
// ==========================================================
const API_URL = "https://d2uab0curhnf0m.cloudfront.net";

// Estado em memória (não usamos localStorage aqui para manter tudo simples;
// isso significa que o login se perde ao recarregar a página)
let token = null;
let emailUsuario = null;
let modoAtual = "login"; // ou "registro"

// Referências aos elementos da página
const tabLogin = document.getElementById("tab-login");
const tabRegistro = document.getElementById("tab-registro");
const formAuth = document.getElementById("form-auth");
const btnAuth = document.getElementById("btn-auth");
const authMensagem = document.getElementById("auth-mensagem");

const authSection = document.getElementById("auth-section");
const tarefasSection = document.getElementById("tarefas-section");
const usuarioLogado = document.getElementById("usuario-logado");
const btnLogout = document.getElementById("btn-logout");

const formTarefa = document.getElementById("form-tarefa");
const listaTarefas = document.getElementById("lista-tarefas");

// ==========================================================
// Alternar entre abas Login / Registro
// ==========================================================
tabLogin.addEventListener("click", () => {
    modoAtual = "login";
    tabLogin.classList.add("active");
    tabRegistro.classList.remove("active");
    btnAuth.textContent = "Entrar";
    authMensagem.textContent = "";
});

tabRegistro.addEventListener("click", () => {
    modoAtual = "registro";
    tabRegistro.classList.add("active");
    tabLogin.classList.remove("active");
    btnAuth.textContent = "Criar conta";
    authMensagem.textContent = "";
});

// ==========================================================
// Enviar formulário de login ou registro
// ==========================================================
formAuth.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    authMensagem.textContent = "";
    authMensagem.className = "mensagem";

    try {
        if (modoAtual === "registro") {
            await registrar(email, senha);
            authMensagem.textContent = "Conta criada! Você já pode fazer login.";
            authMensagem.classList.add("sucesso");
            tabLogin.click();
        } else {
            await login(email, senha);
        }
    } catch (erro) {
        authMensagem.textContent = erro.message;
        authMensagem.classList.add("erro");
    }
});

// ==========================================================
// Chamadas à API — Registro
// ==========================================================
async function registrar(email, senha) {
    const resposta = await fetch(`${API_URL}/registrar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha }),
    });

    if (!resposta.ok) {
        const erro = await resposta.json();
        throw new Error(erro.detail || "Erro ao registrar");
    }
}

// ==========================================================
// Chamadas à API — Login
// ==========================================================
async function login(email, senha) {
    // A rota /login espera um formulário (OAuth2PasswordRequestForm),
    // não JSON — por isso usamos URLSearchParams aqui.
    const corpo = new URLSearchParams();
    corpo.append("username", email);
    corpo.append("password", senha);

    const resposta = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: corpo,
    });

    if (!resposta.ok) {
        const erro = await resposta.json();
        throw new Error(erro.detail || "Email ou senha incorretos");
    }

    const dados = await resposta.json();
    token = dados.access_token;
    emailUsuario = email;

    mostrarTelaTarefas();
    await carregarTarefas();
}

// ==========================================================
// Logout
// ==========================================================
btnLogout.addEventListener("click", () => {
    token = null;
    emailUsuario = null;
    listaTarefas.innerHTML = "";
    tarefasSection.classList.add("hidden");
    authSection.classList.remove("hidden");
    formAuth.reset();
});

function mostrarTelaTarefas() {
    authSection.classList.add("hidden");
    tarefasSection.classList.remove("hidden");
    usuarioLogado.textContent = `Logado como: ${emailUsuario}`;
}

// ==========================================================
// Chamadas à API — Listar tarefas
// ==========================================================
async function carregarTarefas() {
    const resposta = await fetch(`${API_URL}/tarefas`, {
        headers: { Authorization: `Bearer ${token}` },
    });

    if (!resposta.ok) {
        throw new Error("Não foi possível carregar as tarefas");
    }

    const tarefas = await resposta.json();
    renderizarTarefas(tarefas);
}

// ==========================================================
// Renderizar lista de tarefas na tela
// ==========================================================
function renderizarTarefas(tarefas) {
    listaTarefas.innerHTML = "";

    if (tarefas.length === 0) {
        listaTarefas.innerHTML = '<li style="justify-content:center; color:#999;">Nenhuma tarefa ainda</li>';
        return;
    }

    tarefas.forEach((tarefa) => {
        const item = document.createElement("li");
        if (tarefa.concluida) item.classList.add("concluida");

        item.innerHTML = `
      <input type="checkbox" ${tarefa.concluida ? "checked" : ""} data-id="${tarefa.id}" class="checkbox-concluida" />
      <div class="tarefa-info">
        <div class="titulo-tarefa">${escaparHtml(tarefa.titulo)}</div>
        <div class="descricao-tarefa">${escaparHtml(tarefa.descricao)}</div>
      </div>
      <button class="btn-remover" data-id="${tarefa.id}">Remover</button>
    `;

        listaTarefas.appendChild(item);
    });

    // Eventos de marcar como concluída
    document.querySelectorAll(".checkbox-concluida").forEach((checkbox) => {
        checkbox.addEventListener("change", async (evento) => {
            const id = evento.target.getAttribute("data-id");
            await alternarConclusao(id, evento.target.checked);
        });
    });

    // Eventos de remover
    document.querySelectorAll(".btn-remover").forEach((botao) => {
        botao.addEventListener("click", async (evento) => {
            const id = evento.target.getAttribute("data-id");
            await removerTarefa(id);
        });
    });
}

// Evita que texto digitado pelo usuário quebre o HTML da página
function escaparHtml(texto) {
    const div = document.createElement("div");
    div.textContent = texto;
    return div.innerHTML;
}

// ==========================================================
// Chamadas à API — Criar tarefa
// ==========================================================
formTarefa.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const titulo = document.getElementById("titulo").value;
    const descricao = document.getElementById("descricao").value;

    const resposta = await fetch(`${API_URL}/tarefas`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ titulo, descricao, concluida: false }),
    });

    if (resposta.ok) {
        formTarefa.reset();
        await carregarTarefas();
    }
});

// ==========================================================
// Chamadas à API — Atualizar (marcar como concluída)
// ==========================================================
async function alternarConclusao(id, concluida) {
    // Precisamos buscar os dados atuais da tarefa antes de atualizar,
    // já que o PUT espera título e descrição também
    const tarefas = await (await fetch(`${API_URL}/tarefas`, {
        headers: { Authorization: `Bearer ${token}` },
    })).json();

    const tarefaAtual = tarefas.find((t) => t.id == id);
    if (!tarefaAtual) return;

    await fetch(`${API_URL}/tarefas/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            titulo: tarefaAtual.titulo,
            descricao: tarefaAtual.descricao,
            concluida: concluida,
        }),
    });

    await carregarTarefas();
}

// ==========================================================
// Chamadas à API — Remover tarefa
// ==========================================================
async function removerTarefa(id) {
    await fetch(`${API_URL}/tarefas/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });

    await carregarTarefas();
}
