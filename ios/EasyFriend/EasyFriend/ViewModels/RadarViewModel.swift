//
//  RadarViewModel.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import Foundation
import MapKit

enum CriterioRadar: String, CaseIterable, Identifiable {
    case proximidade = "proximidade"
    case idioma = "idioma"
    case pais = "pais"

    var id: String { rawValue }

    var label: String {
        switch self {
        case .proximidade: return "Proxim."
        case .idioma: return "Idioma"
        case .pais: return "País"
        }
    }
}

@MainActor
@Observable
class RadarViewModel {
    var matches: [Match] = []
    var criterio: CriterioRadar = .proximidade
    var isLoading: Bool = false
    var errorMessage: String?

    var regiaoMapa = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: -23.5631, longitude: -46.6544),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )

    func carregarMatches() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let path = "/radar/matches?criterio=\(criterio.rawValue)"
        do {
            matches = try await APIClient.shared.get(path)
        } catch {
            errorMessage = error.localizedDescription
            matches = []
        }
    }

    func mudarCriterio(_ novo: CriterioRadar) async {
        criterio = novo
        await carregarMatches()
    }
}
