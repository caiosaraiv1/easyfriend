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
        idade: 22,
        paisOrigem: "Brasil",
        idiomas: ["PT", "EN"],
        interesses: ["Música", "Culinária", "Tecnologia"],
        email: "isabela@example.com"
    )

    static let usuarios: [Usuario] = [
        Usuario(id: 2, nome: "Ana Silva", idade: 28, paisOrigem: "Brasil",
                idiomas: ["PT", "EN"], interesses: ["Música", "Culinária"], email: nil),
        Usuario(id: 3, nome: "Marco Rossi", idade: 34, paisOrigem: "Itália",
                idiomas: ["IT", "EN", "PT"], interesses: ["Gastronomia", "Esportes"], email: nil),
        Usuario(id: 4, nome: "Yuki Tanaka", idade: 26, paisOrigem: "Japão",
                idiomas: ["JP", "EN"], interesses: ["Arte", "Anime"], email: nil),
        Usuario(id: 5, nome: "Carmen López", idade: 31, paisOrigem: "Espanha",
                idiomas: ["ES", "PT"], interesses: ["Música", "Dança"], email: nil)
    ]

    // MARK: - Matches por criterio (simula o Strategy do backend)

    static func matches(criterio: String) -> [Match] {
        // Centro fixo: Av. Paulista, Sao Paulo (referencia "voce esta aqui")
        let centroLat = -23.5631
        let centroLon = -46.6544

        // Cada criterio retorna uma ordem/subset diferente para mostrar
        // visualmente que o Strategy esta funcionando.
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
            // So usuarios que falam PT
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
        case "pais":
            // So brasileiros (mesmo pais que o usuario atual)
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
                   descricao: "Música e dança da América Latina",
                   tipo: "musica", local: "Parque Ibirapuera",
                   dataInicio: dataDeHoje(adicionando: 5),
                   interessados: 42),
            Evento(id: 2, titulo: "Roda de Samba",
                   descricao: "Roda aberta com músicos da comunidade",
                   tipo: "musica", local: "Vila Madalena",
                   dataInicio: dataDeHoje(adicionando: 8),
                   interessados: 15),
            Evento(id: 3, titulo: "Concerto Coreano",
                   descricao: "Apresentação de música tradicional coreana",
                   tipo: "musica", local: "MASP",
                   dataInicio: dataDeHoje(adicionando: 12),
                   interessados: 8),
            Evento(id: 4, titulo: "Feira Italiana",
                   descricao: "Comidas e doces típicos italianos",
                   tipo: "gastronomia", local: "Bixiga",
                   dataInicio: dataDeHoje(adicionando: 3),
                   interessados: 67),
            Evento(id: 5, titulo: "Exposição Japonesa",
                   descricao: "Arte contemporânea japonesa",
                   tipo: "arte", local: "Pinacoteca",
                   dataInicio: dataDeHoje(adicionando: 15),
                   interessados: 23)
        ]
        guard let filtro = tipoFiltro else { return todos }
        return todos.filter { $0.tipo == filtro }
    }

    private static func dataDeHoje(adicionando dias: Int) -> Date {
        Calendar.current.date(byAdding: .day, value: dias, to: Date()) ?? Date()
    }
}
