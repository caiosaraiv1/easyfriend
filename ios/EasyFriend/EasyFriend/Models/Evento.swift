//
//  Evento.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//


import Foundation

struct Evento: Codable, Identifiable {
    let id: Int
    let titulo: String
    let descricao: String
    let tipo: String        // "musica", "gastronomia", "arte", etc.
    let local: String
    let dataInicio: Date
    let interessados: Int
}

// Tipos de evento disponiveis para filtrar.
// O case rawValue precisa bater com o que o backend devolve em `tipo`.
enum TipoEvento: String, CaseIterable, Identifiable {
    case musica = "musica"
    case gastronomia = "gastronomia"
    case arte = "arte"

    var id: String { rawValue }

    var label: String {
        switch self {
        case .musica: return "Música"
        case .gastronomia: return "Gastro"
        case .arte: return "Arte"
        }
    }
}
