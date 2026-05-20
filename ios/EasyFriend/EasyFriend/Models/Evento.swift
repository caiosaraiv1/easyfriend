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

    //Helpers com defaults para usar nas Views sem nil-checks
    var descricaoExibida: String { descricao ?? "" }
    var localExibido: String { local ?? "Local a confirmar" }
    var interessadosExibidos: Int { interessados ?? 0 }
    
    enum CodingKeys: String, CodingKey {
        case id
        case titulo
        case tipo
        case dataInicio = "data_inicio"
        case descricao
        case local
        case interessados
    }
}

//tipos de evento disponiveis
//rawValue precisa bater com o que o backend devolve em `tipo`.
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
