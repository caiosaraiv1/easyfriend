//
//  RadarScreen.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI
import MapKit

struct RadarScreen: View {
    // @State substitui @StateObject.
    @State private var viewModel = RadarViewModel()
    @State private var matchSelecionado: Match?

    var body: some View {
        // @Bindable habilita o uso de $ para criar bindings com @Observable.
        @Bindable var viewModel = viewModel

        NavigationStack {
            VStack(spacing: 0) {
                Picker("Critério", selection: $viewModel.criterio) {
                    ForEach(CriterioRadar.allCases) { criterio in
                        Text(criterio.label).tag(criterio)
                    }
                }
                .pickerStyle(.segmented)
                .padding()
                .onChange(of: viewModel.criterio) { _, novo in
                    Task { await viewModel.mudarCriterio(novo) }
                }

                if viewModel.isLoading {
                    ProgressView("Buscando...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let erro = viewModel.errorMessage {
                    VStack(spacing: 8) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundStyle(.secondary)
                        Text(erro)
                            .multilineTextAlignment(.center)
                            .foregroundStyle(.secondary)
                        Button("Tentar novamente") {
                            Task { await viewModel.carregarMatches() }
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    mapa
                }
            }
            .navigationTitle("Radar")
            .navigationBarTitleDisplayMode(.inline)
            .task {
                if viewModel.matches.isEmpty {
                    await viewModel.carregarMatches()
                }
            }
            .sheet(item: $matchSelecionado) { match in
                DetalheMatchScreen(match: match)
            }
        }
    }

    private var mapa: some View {
        Map(initialPosition: .region(viewModel.regiaoMapa)) {
            Annotation("Você", coordinate: viewModel.regiaoMapa.center) {
                Circle()
                    .fill(.blue)
                    .frame(width: 16, height: 16)
                    .overlay(
                        Circle()
                            .stroke(.white, lineWidth: 2)
                    )
            }

            ForEach(viewModel.matches) { match in
                MapCircle(center: match.coordenada,
                          radius: match.raioPrivacidadeMetros)
                    .foregroundStyle(.blue.opacity(0.15))
                    .stroke(.blue.opacity(0.6), lineWidth: 1)

                Annotation(match.usuario.nome, coordinate: match.coordenada) {
                    Button {
                        matchSelecionado = match
                    } label: {
                        Text(match.inicial)
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundStyle(.white)
                            .frame(width: 28, height: 28)
                            .background(Color.blue)
                            .clipShape(Circle())
                    }
                }
            }
        }
    }
}

#Preview {
    RadarScreen()
}
