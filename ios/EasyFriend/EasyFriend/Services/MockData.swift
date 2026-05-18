//
//  MockData.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

//TODO: - Apagar depois

import Foundation

enum MockData {

    // MARK: - Usuarios

    static let usuarioAtual = Usuario(
        id: 1,
        nome: "Isabela Hissa",
        paisOrigem: "Brasil",
        idade: 22,
        idioma: "pt",
        idiomas: ["pt", "en"],
        interesses: ["Música", "Culinária", "Tecnologia"],
        email: "isabela@example.com"
    )

    static let usuarios: [Usuario] = [
        Usuario(id: 2, nome: "Ana Silva", paisOrigem: "Brasil",
                idade: 28, idioma: "pt",
                idiomas: ["pt", "en"], interesses: ["Música", "Culinária"]),
        Usuario(id: 3, nome: "Marco Rossi", paisOrigem: "Itália",
                idade: 34, idioma: "it",
                idiomas: ["it", "en", "pt"], interesses: ["Gastronomia", "Esportes"]),
        Usuario(id: 4, nome: "Yuki Tanaka", paisOrigem: "Japão",
                idade: 26, idioma: "ja",
                idiomas: ["ja", "en"], interesses: ["Arte", "Anime"]),
        Usuario(id: 5, nome: "Carmen López", paisOrigem: "Espanha",
                idade: 31, idioma: "es",
                idiomas: ["es", "pt"], interesses: ["Música", "Dança"])
    ]

    // MARK: - Matches por criterio

    static func matches(criterio: String) -> [Match] {
        let centroLat = -23.5631
        let centroLon = -46.6544

        switch criterio {
        case "proximidade":
            return [
                Match(id: 1, usuario: usuarios[0],
                      coordenadaLat: centroLat + 0.008, coordenadaLon: centroLon + 0.005,
                      raioPrivacidadeMetros: 300, distanciaKm: 1.2,
                      criadoEm: Date()),
                Match(id: 2, usuario: usuarios[1],
                      coordenadaLat: centroLat - 0.015, coordenadaLon: centroLon - 0.010,
                      raioPrivacidadeMetros: 500, distanciaKm: 2.8,
                      criadoEm: Date()),
                Match(id: 3, usuario: usuarios[2],
                      coordenadaLat: centroLat + 0.020, coordenadaLon: centroLon + 0.025,
                      raioPrivacidadeMetros: 700, distanciaKm: 3.5,
                      criadoEm: Date())
            ]
        case "idioma":
            return [
                Match(id: 1, usuario: usuarios[0],
                      coordenadaLat: centroLat + 0.008, coordenadaLon: centroLon + 0.005,
                      raioPrivacidadeMetros: 300, distanciaKm: 1.2,
                      criadoEm: Date()),
                Match(id: 2, usuario: usuarios[1],
                      coordenadaLat: centroLat - 0.015, coordenadaLon: centroLon - 0.010,
                      raioPrivacidadeMetros: 500, distanciaKm: 2.8,
                      criadoEm: Date()),
                Match(id: 4, usuario: usuarios[3],
                      coordenadaLat: centroLat - 0.020, coordenadaLon: centroLon + 0.012,
                      raioPrivacidadeMetros: 400, distanciaKm: 2.4,
                      criadoEm: Date())
            ]
        case "pais", "pais_origem":
            return [
                Match(id: 1, usuario: usuarios[0],
                      coordenadaLat: centroLat + 0.008, coordenadaLon: centroLon + 0.005,
                      raioPrivacidadeMetros: 300, distanciaKm: 1.2,
                      criadoEm: Date())
            ]
        default:
            return []
        }
    }

    // MARK: - Eventos

    static func eventos(tipoFiltro: String?) -> [Evento] {
        let todos = [
            Evento(id: 1, titulo: "Festival Latino",
                   tipo: "musica",
                   dataInicio: dataDeHoje(adicionando: 5),
                   descricao: "Música e dança da América Latina",
                   local: "Parque Ibirapuera",
                   interessados: 42),
            Evento(id: 2, titulo: "Roda de Samba",
                   tipo: "musica",
                   dataInicio: dataDeHoje(adicionando: 8),
                   descricao: "Roda aberta com músicos da comunidade",
                   local: "Vila Madalena",
                   interessados: 15),
            Evento(id: 3, titulo: "Concerto Coreano",
                   tipo: "musica",
                   dataInicio: dataDeHoje(adicionando: 12),
                   descricao: "Apresentação de música tradicional coreana",
                   local: "MASP",
                   interessados: 8),
            Evento(id: 4, titulo: "Feira Italiana",
                   tipo: "gastronomia",
                   dataInicio: dataDeHoje(adicionando: 3),
                   descricao: "Comidas e doces típicos italianos",
                   local: "Bixiga",
                   interessados: 67),
            Evento(id: 5, titulo: "Exposição Japonesa",
                   tipo: "arte",
                   dataInicio: dataDeHoje(adicionando: 15),
                   descricao: "Arte contemporânea japonesa",
                   local: "Pinacoteca",
                   interessados: 23)
        ]
        guard let filtro = tipoFiltro else { return todos }
        return todos.filter { $0.tipo == filtro }
    }

    private static func dataDeHoje(adicionando dias: Int) -> Date {
        Calendar.current.date(byAdding: .day, value: dias, to: Date()) ?? Date()
    }
}
