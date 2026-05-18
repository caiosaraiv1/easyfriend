//
//  AgendaViewModel.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import Foundation

@MainActor
@Observable
class AgendaViewModel {
    var eventos: [Evento] = []
    var tipoSelecionado: TipoEvento = .musica
    var isLoading: Bool = false
    var errorMessage: String?

    func carregarEventos() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let path = "/agenda/eventos?criterio=tipo&valor=\(tipoSelecionado.rawValue)"
        do {
            eventos = try await APIClient.shared.get(path)
        } catch {
            errorMessage = error.localizedDescription
            eventos = []
        }
    }

    func mudarTipo(_ novo: TipoEvento) async {
        tipoSelecionado = novo
        await carregarEventos()
    }
}
