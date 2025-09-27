import random
import re

class Wezel:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.czas = 0
        self.procesor = None
        self.typ_przydzialu = None
        self.rozpoczecie = None
        self.krawedzie = []

    def dodaj_krawedz(self, wezel, przepustowosc):
        self.krawedzie.append((wezel, przepustowosc))

class Graf:
    def __init__(self):
        self.wezly = {}
        self.czasy = []
        self.koszty = []
        self.procesory = []
        self.stala_przesylu = 1
        self.koszt_polaczenia = 0
        self.dostepnosc_procesorow = []
        self.calkowity_koszt = 0
        self.proc = []
        self.kara = []
        self.limit_miekki_czas = 0
        self.rozwiazania = []

    def dodaj_wezel(self, nazwa):
        if nazwa not in self.wezly:
            self.wezly[nazwa] = Wezel(nazwa)

    def dodaj_krawedz(self, start, koniec, przepustowosc):
        if start in self.wezly and koniec in self.wezly:
            self.wezly[start].dodaj_krawedz(self.wezly[koniec], przepustowosc)

    def jaki_limit_czas(self):
        number = float(input("Jaki maksymalny czas wykonania? "))
        self.limit_miekki_czas = number

    def wczytaj_dane_file1(self, plik):
        with open(plik, 'r') as f:
            linie = [l.strip() for l in f.readlines() if l.strip()]
        idx = 0
        while idx < len(linie):
            line = linie[idx]
            if line.startswith('@tasks'):
                n = int(line.split()[1])
                for i in range(1, n + 1):
                    parts = linie[idx + i].split()
                    nazwa = parts[0]
                    self.dodaj_wezel(nazwa)
                for i in range(1, n + 1):
                    parts = linie[idx + i].split()
                    nazwa = parts[0]
                    dzieci = parts[2:]
                    for d in dzieci:
                        match = re.match(r'(\d+)\((\d+)\)', d)
                        if match:
                            # Poprawione dopasowanie nazwy dziecka
                            d_nazwa = f"T{match.group(1)}"
                            przepust = int(match.group(2))
                            self.dodaj_krawedz(nazwa, d_nazwa, przepust)
                idx += n + 1
            elif line.startswith('@proc'):
                m = int(line.split()[1])
                idx += 1
                for i in range(m):
                    self.procesory.append(list(map(int, linie[idx].split())))
                    idx += 1
                self.proc = [0] * len(self.procesory)
                self.dostepnosc_procesorow = [0] * len(self.procesory)
            elif line.startswith('@times'):
                idx += 1
                while idx < len(linie) and not linie[idx].startswith('@'):
                    self.czasy.append(list(map(int, linie[idx].split())))
                    idx += 1
            elif line.startswith('@cost'):
                idx += 1
                while idx < len(linie) and not linie[idx].startswith('@'):
                    self.koszty.append(list(map(int, linie[idx].split())))
                    idx += 1
            elif line.startswith('@comm'):
                idx += 1
                if idx < len(linie):
                    comm_info = linie[idx].split()
                    if len(comm_info) >= 3:
                        self.koszt_polaczenia = int(comm_info[1])
                        self.stala_przesylu = int(comm_info[2])
                        idx += 1
            else:
                idx += 1

    def wczytaj_dane_file2(self, plik):
        with open(plik, 'r') as f:
            linie = [l.strip() for l in f.readlines() if l.strip()]
        for line in linie:
            parts = line.split(":")
            procesor = parts[0].strip()
            zadania = parts[1].split(",")
            for zadanie in zadania:
                zadanie = zadanie.strip()
                match = re.match(r'(T\d+)\((\d+)\)', zadanie)
                if match:
                    task_name = match.group(1)
                    time = int(match.group(2))
                    self.dodaj_wezel(task_name)
                    task = self.wezly[task_name]
                    task.czas = time
                    task.procesor = procesor
                else:
                    match_ut = re.match(r'(UT\d+)', zadanie)
                    if match_ut:
                        task_name = match_ut.group(1)
                        self.dodaj_wezel(task_name)
                        task = self.wezly[task_name]
                        task.czas = 0
                        task.procesor = None

    def znajdz_typy_i_przydziel(self):
        for wezel in self.wezly.values():
            if wezel.procesor and wezel.procesor.startswith("P"):
                try:
                    proc_index = int(wezel.procesor[1:])
                except ValueError:
                    proc_index = None
                if proc_index is not None and proc_index < len(self.procesory):
                    if self.procesory[proc_index][1] == 0 and self.procesory[proc_index][2] == 0:
                        wezel.typ_przydzialu = "Z"
                    else:
                        wezel.typ_przydzialu = "T"
                else:
                    # Obsługa przypadku, gdy indeks procesora jest poza zakresem
                    print(f"Warning: procesor '{wezel.procesor}' poza zakresem lub nieprawidłowy indeks")
                    wezel.typ_przydzialu = "UT"
            else:
                wezel.typ_przydzialu = "UT"

    def oblicz_czasy(self):
        self.czas_procesora = {i: 0 for i in range(len(self.procesory))}
        t_wezly = [w for w in self.wezly.values() if w.typ_przydzialu == "T"]

        for wezel in self.wezly.values():
            if wezel.typ_przydzialu == "T":
                proc_index = int(wezel.procesor[1:])
                task_index = int(wezel.nazwa[1:])
                wezel.czas = self.czasy[task_index][proc_index]
                wezel.rozpoczecie = self.czas_procesora[proc_index]
                self.czas_procesora[proc_index] += wezel.czas

            elif wezel.typ_przydzialu == "UT":
                dozwolone_procesory = [i for i, p in enumerate(self.procesory) if p[1] == 0 and p[2] == 1]
                if dozwolone_procesory:
                    losowy_index = random.choice(dozwolone_procesory)
                    wezel.procesor = f"P{losowy_index}"

                        # Średnia czasu z losowych zadań typu T
                    if len(t_wezly) >= 3:
                        losowe_t_wezly = random.sample(t_wezly, 3)
                    else:
                        losowe_t_wezly = t_wezly

                    task_indexes = [int(t.nazwa[1:]) for t in losowe_t_wezly]
                    srednia_czas = round(
                     sum(self.czasy[task_index][losowy_index] for task_index in task_indexes) / len(task_indexes)
                        )
                    task_indexes = [int(tw.nazwa[1:]) for tw in losowe_t_wezly]

                    srednia_koszt = round(sum(self.koszty[ti][proc_index] for ti in task_indexes) / len(task_indexes))

                    self.calkowity_koszt += srednia_koszt

                    wezel.czas = srednia_czas
                    wezel.rozpoczecie = self.czas_procesora[losowy_index]
                    self.czas_procesora[losowy_index] += wezel.czas


    def oblicz_koszt(self):
        self.calkowity_koszt = 0
        uzyte_procesory = set()
        t_wezly = [w for w in self.wezly.values() if w.typ_przydzialu == "T"]

        for wezel in self.wezly.values():
            if wezel.procesor and wezel.procesor.startswith("P"):
                proc_index = int(wezel.procesor[1:])
                uzyte_procesory.add(proc_index)

                if wezel.nazwa.startswith("T"):
                    task_index = int(wezel.nazwa[1:])
                    self.calkowity_koszt += self.koszty[task_index][proc_index]

                elif wezel.nazwa.startswith("UT"):
                    if len(t_wezly) >= 3:
                        losowe_t_wezly = random.sample(t_wezly, 3)
                    else:
                        losowe_t_wezly = t_wezly
                    

        for proc_index in uzyte_procesory:
            self.calkowity_koszt += self.procesory[proc_index][0]

    def oblicz_kara(self, i, l):
        k = 0
        maks_czas = max(self.czas_procesora.values())
        if maks_czas > self.limit_miekki_czas:
            h = maks_czas - self.limit_miekki_czas
            k += h * l
        self.kara.append(k)

    def wypisz_rozwiazania(self):
        posortowane = sorted(self.rozwiazania, key=lambda r: r["koszt"])
        print("\n--- Posortowane rozwiązania ---")
        for r in posortowane:
            print(f"Rozwiązanie {r['numer']}: czas = {r['czas']}, kara = {r['kara']:.2f}, koszt bez kary = {r['koszt_bez_kary']}, koszt = {r['koszt']}")
            for nazwa, dane in r["wezly"].items():
                print(f"  {nazwa}: Procesor = {dane[0]}, Czas = {dane[1]}, Typ = {dane[2]}")
            print()
    def evaluate_individual(self, individual):
        koszt = 0
        czas_sum = 0
        uzyte_procesory = set()

        # Przygotowanie listy T do wyliczania srednich kosztow dla UT
        t_wezly = [w for w in self.wezly.values() if w.typ_przydzialu == "T"]
        if len(t_wezly) >= 3:
            losowe_t_indexy = random.sample([int(w.nazwa[1:]) for w in t_wezly], 3)
        elif t_wezly:
            losowe_t_indexy = [int(w.nazwa[1:]) for w in t_wezly]
        else:
            losowe_t_indexy = []

        for nazwa, w in individual.items():
            proc_index = int(w.procesor[1:])
            uzyte_procesory.add(proc_index)
            czas_sum += w.czas

            if w.typ_przydzialu == "T" or w.nazwa.startswith("T"):
                task_index = int(w.nazwa[1:])
                koszt += self.koszty[task_index][proc_index]

            elif w.typ_przydzialu == "UT" or w.nazwa.startswith("UT"):
                if losowe_t_indexy:
                    srednia_koszt = round(sum(self.koszty[i][proc_index] for i in losowe_t_indexy) / len(losowe_t_indexy))
                    koszt += srednia_koszt

        # Koszt użycia procesorów
        for proc_index in uzyte_procesory:
            koszt += self.procesory[proc_index][0]

        # Kara za przekroczenie limitu czasu
        kara = max(0, czas_sum - self.limit_miekki_czas) * (self.kara[0] if self.kara else 0)

        # Komunikacja między zadaniami na różnych procesorach
        for w in self.wezly.values():
            for (sasiad, koszt_krawedzi) in w.krawedzie:
                if individual[w.nazwa].procesor != individual[sasiad.nazwa].procesor:
                    koszt += koszt_krawedzi * self.koszt_polaczenia

        return {
            "koszt": koszt + kara,
            "kara": kara,
            "czas": czas_sum,
            "koszt_bez_kary": koszt
        }


    def generate_individual(self):
        individual = {}

        # Lista zadań typu T, z których będziemy losować dla UT
        t_wezly = [w for w in self.wezly.values() if w.typ_przydzialu == "T"]

        for w in self.wezly.values():
            typ = w.typ_przydzialu

            # Dobór dopuszczalnych procesorów
            if typ == "Z":
                allowed = [i for i, p in enumerate(self.procesory) if p[1] == 0]
            elif typ == "UT":
                allowed = [i for i, p in enumerate(self.procesory) if p[2] == 1]
            else:  # typ == "T"
                allowed = list(range(len(self.procesory)))

            # Losowy wybór procesora z dopuszczalnych
            proc_index = random.choice(allowed)
            proc = f"P{proc_index}"

            # Stwórz nowy węzeł na podstawie oryginału
            nowy = Wezel(w.nazwa)
            nowy.procesor = proc
            nowy.typ_przydzialu = typ

            # Ustal czas wykonania
            if typ == "UT":
                if len(t_wezly) >= 3:
                    losowe_t = random.sample(t_wezly, 3)
                elif len(t_wezly) > 0:
                    losowe_t = t_wezly
                else:
                    # Awaryjne przypisanie czasu, gdy nie ma żadnych T
                    nowy.czas = 10
                    individual[w.nazwa] = nowy
                    continue

                # Oblicz średni czas dla UT na podstawie T
                task_indexes = [int(t.nazwa[1:]) for t in losowe_t]
                nowy.czas = round(sum(self.czasy[ti][proc_index] for ti in task_indexes) / len(task_indexes))
            else:
                nowy.czas = w.czas  # Przepisz oryginalny czas

            individual[w.nazwa] = nowy

        return individual


    def simulate_population(self, n=20):
        population = []
        for _ in range(n):
            indiv = self.generate_individual()
            eval_res = self.evaluate_individual(indiv)
            population.append((indiv, eval_res))
        return population

    def crossover_individuals(self, parent1, parent2):
        child = {}
        for w in parent1:
            chosen = random.choice([parent1[w], parent2[w]])
            child[w] = Wezel(w)
            child[w].czas = chosen.czas
            child[w].procesor = chosen.procesor
            child[w].typ_przydzialu = chosen.typ_przydzialu
        return child

    def unikaty_rozwiazania(self, lista):
        unikalne = []
        seen = set()
        for indiv, wyn in lista:
            key = (
                wyn['koszt'],
                wyn['kara'],
                wyn['czas'],
                tuple(sorted((nazwa, w.procesor) for nazwa, w in indiv.items()))
            )
            if key not in seen:
                seen.add(key)
                unikalne.append((indiv, wyn))
        return unikalne

    def run_evolution(self, generations=10, pop_size=20, n_klony=5, n_mutacje=5, n_krzyz=10, top_k=5):
        population = self.simulate_population(pop_size)

        for gen in range(generations):
            population.sort(key=lambda x: x[1]["koszt"])
            weights = list(range(len(population), 0, -1))

            def select():
                return copy.deepcopy(random.choices(population, weights=weights, k=1)[0][0])

            new_population = []

            for _ in range(n_klony):
                indiv = select()
                eval_res = self.evaluate_individual(indiv)
                new_population.append((indiv, eval_res))

            for _ in range(n_mutacje):
                indiv = select()
                for w in indiv.values():
                    if w.typ_przydzialu in ("UT", "Z"):
                        allowed = [i for i, p in enumerate(self.procesory) if p[1] == 0 and p[2] == 1]
                        if allowed:
                            proc = random.choice(allowed)
                            w.procesor = f"P{proc}"
                eval_res = self.evaluate_individual(indiv)
                new_population.append((indiv, eval_res))

            for _ in range(n_krzyz):
                p1 = select()
                p2 = select()
                child = self.crossover_individuals(p1, p2)
                eval_res = self.evaluate_individual(child)
                new_population.append((child, eval_res))

            population = new_population

            
            best = sorted(population, key=lambda x: x[1]["koszt"])[:3]
            

        print(f"\n=== Najlepsze {top_k} unikalnych rozwiązań z ostatniego pokolenia ===")
        population.sort(key=lambda x: x[1]["koszt"])
        unikalne_rozw = self.unikaty_rozwiazania(population)
        for i, (indiv, wyn) in enumerate(unikalne_rozw[:top_k]):
            print(f"\nRozwiązanie {i}: koszt={wyn['koszt']}, kara={wyn['kara']}, czas={wyn['czas']}")
            print("Szczegóły przydziałów:")
            for nazwa, w in indiv.items():
                print(f"  {nazwa}: Procesor = {w.procesor}, Czas = {w.czas}, Typ = {w.typ_przydzialu}")
# --- URUCHOMIENIE ---
if __name__ == "__main__":
    import copy  # potrzebne dla deepcopy w metodzie run_evolution

    # Wczytanie danych z plików
    plik1 = 'graph10.txt'
    plik2 = 'architektura.txt'

    graf = Graf()
    graf.wczytaj_dane_file1(plik1)
    graf.wczytaj_dane_file2(plik2)
    graf.znajdz_typy_i_przydziel()

    # Parametry użytkownika
    graf.jaki_limit_czas()
    waga_kary = float(input("Kara to ile razy różnica między limitem czasu, a czasem wykonania? "))
    graf.kara.append(waga_kary)  # przechowujemy wagę, by użyć jej w evaluate_individual

    # Parametry ewolucji
    generacje = int(input("Ile pokoleń ewolucji? "))
    populacja = int(input("Ile osobników w każdej populacji? "))
    klony = int(input("Ile klonów wybierać? "))
    mutacje = int(input("Ile osobników mutować? "))
    krzyzowania = int(input("Ile par krzyżować? "))
    top_k = int(input("Ile najlepszych rozwiązań wypisać na końcu? "))

    # Uruchomienie algorytmu ewolucyjnego
    graf.run_evolution(
        generations=generacje,
        pop_size=populacja,
        n_klony=klony,
        n_mutacje=mutacje,
        n_krzyz=krzyzowania,
        top_k=top_k
    )
