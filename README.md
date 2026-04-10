# Enhetstestning med Mock och Stub
## Syfte

Vid enhetstestning testar vi en komponent i isolation.  
Eftersom kod ofta beror på externa system (t.ex. API:er eller databaser) ersätts dessa med test doubles.

De två viktigaste typerna är:

- Stub: ger förutsägbara svar
- Mock: kontrollerar hur något anropas

---

## Stub vs Mock

| Egenskap | Stub | Mock |
|----------|------|------|
| Syfte | Ge ett svar | Verifiera anrop |
| Fokus | Resultat | Beteende |
| Assertion | assert result == x | assert_called_* |

---
 

## System

| Klass | Roll |
|------|------|
| OrderService | Det vi testar |
| PaymentGateway | Externt beroende |
| EmailNotifier | Externt beroende |

Beroenden skickas in via konstruktorn (Dependency Injection).

---
## Hur testerna körs 
```` python
pytest tests/ -v
````

## Deltagare 
Moaz Ameer & Sadaq keynaan