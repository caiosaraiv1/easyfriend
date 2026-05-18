//
//  AgendaScreen.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

struct AgendaScreen: View {
    @State private var viewModel = AgendaViewModel()

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 0) {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(TipoEvento.allCases) { tipo in
                            chip(tipo: tipo)
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)

                if viewModel.isLoading {
                    Spacer()
                    ProgressView("Carregando eventos...")
                    Spacer()
                } else if viewModel.eventos.isEmpty {
                    Spacer()
                    Text("Nenhum evento encontrado")
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity)
                    Spacer()
                } else {
                    List(viewModel.eventos) { evento in
                        EventoRow(evento: evento)
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("Agenda")
            .task {
                if viewModel.eventos.isEmpty {
                    await viewModel.carregarEventos()
                }
            }
        }
    }

    private func chip(tipo: TipoEvento) -> some View {
        let selecionado = viewModel.tipoSelecionado == tipo
        return Text(tipo.label)
            .font(.caption)
            .fontWeight(selecionado ? .semibold : .regular)
            .padding(.horizontal, 14)
            .padding(.vertical, 6)
            .background(selecionado ? Color.blue : Color.gray.opacity(0.15))
            .foregroundStyle(selecionado ? .white : .primary)
            .clipShape(Capsule())
            .onTapGesture {
                Task { await viewModel.mudarTipo(tipo) }
            }
    }
}

struct EventoRow: View {
    let evento: Evento

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(evento.titulo)
                .font(.headline)
            HStack(spacing: 6) {
                Image(systemName: "calendar")
                    .font(.caption2)
                Text(dataFormatada(evento.dataInicio))
                Text("·")
                Text(evento.localExibido)
            }
            .font(.caption)
            .foregroundStyle(.secondary)
            if evento.interessadosExibidos > 0 {
                Text("\(evento.interessadosExibidos) interessados")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }

    private func dataFormatada(_ data: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "pt_BR")
        formatter.dateFormat = "d MMM"
        return formatter.string(from: data)
    }
}

#Preview {
    AgendaScreen()
}
