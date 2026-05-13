//
//  EasyFriendApp.swift
//  EasyFriend
//
//  Created by Isabela Hissa Pinto on 12/05/26.
//

import SwiftUI

@main
struct EasyFriendApp: App {
    // Com @Observable, usa-se @State em vez de @StateObject.
    @State private var authViewModel = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            // Injeta no environment via .environment() (sem o "Object" no final).
            ContentView()
                .environment(authViewModel)
        }
    }
}
