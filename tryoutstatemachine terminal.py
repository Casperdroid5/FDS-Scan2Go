class StateMachine:
    def __init__(self):
        self.current_state = None

    def set_state(self, state):
        self.current_state = state

    def run(self):
        while True:
            self.current_state.execute(self)


class Door1Unlocked:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Deur 1: Ontgrendeld")
        print("Deur 2: Vergrendeld")
        print("\nMogelijke acties:")
        print("1. Handmatig sluiten van Deur 1")
        print("2. Ruimte weer verlaten")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            statemachine.set_state(Door1UnlockedWithPerson())
        elif choice == "2":
            print("Programma gestopt.")
            return
        else:
            print("Ongeldige keuze. Probeer opnieuw.")


class Door1UnlockedWithPerson:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Persoon gedetecteerd in gebied A en Deur 1 gesloten")
        print("\nMogelijke acties:")
        print("1. Vergrendelen van Deur 1")
        print("2. Ruimte verlaten")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            statemachine.set_state(FerrometalDetection())
        elif choice == "2":
            statemachine.set_state(Door1Unlocked())
        else:
            print("Ongeldige keuze. Probeer opnieuw.")


class FerrometalDetection:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Ferrometaaldetectie wordt uitgevoerd")
        print("\nMogelijke acties:")
        print("1. Ferrometaal wordt NIET gedetecteerd")
        print("2. Ferroemtaal wordt WEL gedetecteerd")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            print("1. Ferrometaal NIET gedetecteerd u kunt verder gaan naar de MRI-ruimte door deur 2.")
            statemachine.set_state(Door2UnlockedWithPerson())
        elif choice == "2":
            print("Ferroemtaal gedetecteerd, verwijder aub alle ferrometalen in de kleedruimte en probeer het opnieuw.")
            statemachine.set_state(Door1UnlockedWithPerson())
        else:
            print("Ongeldige keuze. Probeer opnieuw.")


class Door2UnlockedWithPerson:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Deur 2 ontgrendeld")
        print("\nMogelijke acties:")
        print("1. Verlaat FDS door deur 2 naar MRI-Ruimte. ")
        print("2. Verzoek FDS door deur 1 naar de kleedkamer te kunnen")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            statemachine.set_state(Door2Unlocked())
        elif choice == "2":
            print("Programma gestopt.")
            return
        else:
            print("Ongeldige keuze. Probeer opnieuw.")
            
class Door2Unlocked:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Deur 2 ontgrendeld")
        print("\nMogelijke acties:")
        print("1. Patient keert terug naar FDS")
        print("2.")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            print("1. Patiënt keert terug naar FDS")
            statemachine.set_state(Door2Locked())
        elif choice == "2":
            #statemachine.set_state(Door1UnlockedWithPerson())            
            print("Programma gestopt.")
            return
        else:
            print("Ongeldige keuze. Probeer opnieuw.")          
            
class Door2Locked:
    def __init__(self):
        pass

    def execute(self, statemachine):
        print("Deur 2 ontgrendeld")
        print("\nMogelijke acties:")
        print("1. Patiënt sluit deur 2")
        print("2. ")
        choice = input("Voer uw keuze in: ")
        if choice == "1":
            print("1. Deur 2 wordt vergrendeld en deur 1 ontgrendeld ")
            statemachine.set_state(Door1Unlocked())
        elif choice == "2":
            #statemachine.set_state(Door1UnlockedWithPerson())            
            print("Programma gestopt.")
            return
        else:
            print("Ongeldige keuze. Probeer opnieuw.")       


if __name__ == "__main__":
    sm = StateMachine()
    sm.set_state(Door1Unlocked())
    sm.run()
