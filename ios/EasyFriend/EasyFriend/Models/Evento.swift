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
    let tipo: String
    let dataInicio: Date

    //campos opcionais
    let descricao: String?
    let local: String?
    let interessados: Int?

    //Helpers com defaults
    var descricaoExibida: String { descricao ?? "" }
    var localExibido: String { local ?? "Local a confirmar" }
    var interessadosExibidos: Int { interessados ?? 0 }
}

// Tipos de evento disponiveis para filtrar.
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