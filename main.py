FILE_LL = "ll.txt"
FILE_LR = "lr.txt"
FILE_INPUT = "input.txt"

EPSILON = 'ϵ'


def read_input_file(file_name):
    with open(file_name) as f: # input dosyasını acıyoruz 
        lines = f.readlines()  
        data_lines = lines[1:] # ilk satır header ve ise yaramıyor direkt attık 1: olarak okuduk alt satırdan
        data = [tuple(line.strip().split(';')) for line in data_lines if line.strip()]
       # inputları tuple olarak aldık ;dan böldük ve sonra her line için stirp yaptık boslukları atmak icin
    return data



def read_ll_table(file_name):
    with open(file_name) as f:
        lines = [line.strip().split(';') for line in f.readlines()]# yine ;dan böldük ve boslukları strip ile attık
    header = [col.strip() for col in lines[0][1:]] # ilk satırı header olarak attık ancak table typeı almadık
    data = {line[0].strip(): {k.strip(): v.replace('Ïµ', EPSILON).replace('ϵ',EPSILON).strip() for k, v in zip(header, line[1:])} for line in lines[1:]}
         # nested dict olusturduk ilk dict satır basını key olarak tutuyor value icerideki keyvalue ciftleri
         #icerideki dictte ise header degelrei key icinde de asıl valuelar var boylece stackten okuma yapınca dictten rahatca okuyabiliyoruz
         #epsilon karakterini düzgün basamıyordu replace yaptık her deger icin strip kullandıkprint(data)
    return data

def get_terminals(ll_table): #eslestirme yapabilmek icin tablodan terminalleri cekmemiz lazımdı ki mesela id iyi okunsun
    terminals = set() 
    for non_terminal in ll_table: # nested dict okuma icin for dongusu
        for terminal in ll_table[non_terminal]:
            terminals.add(terminal)
    terminals.discard(EPSILON) # epsilonun kontrolu zaten ayrı olarak processde yapılıyo
    return sorted(terminals)


def tokenize_input(input_str, terminals):
    tokens = []
    buffer = ''#karakterleri gcici tutacak
    for char in input_str:# basladık input okumaya
        buffer += char# okunanı buffera ekledik
        if buffer in terminals: # yukarıda buldugumuz terminallerde varsa o zaman bu artık token/lexemedir 
            tokens.append(buffer)
            buffer = ''# buffer bosalttık
    return tokens

def process_ll(input_str, ll_table):
    stack = ['$']
    terminals = get_terminals(ll_table)
    input_tokens = tokenize_input(input_str, terminals)
    print("NO | STACK | INPUT | ACTION")
    step = 1

    stack.append(list(ll_table.keys())[0]) #ilk kuraldan baslama özel durumu 

    while stack:
        current_state = stack[-1] #stack tepeden al ve inputun tepeden al 
        current_input = input_tokens[0]

        if current_state in ll_table.keys() and current_input in ll_table[current_state]:
            action = ll_table[current_state][current_input] # tabloda bunlara karsılık gelen durum var mı kontrolu
           
            if action:
                print(f"{step} | {''.join(stack)} | {''.join(input_tokens)} | {action}")#formatlı yazdırıyoruz
                new_states = action.split("->")[1].strip().split()#gelen actionu oktan bölüyoruz ve space varsa atıyoz
                stack.pop()  # actionunu yaptıgımız terminali cıkarıyoz artık
                for s in reversed(new_states): # ters donduruup durumun karakterleri okunur
                    if s != EPSILON: #epsilon veya terminal degilse stacke tersten ekleme yapılır 
                        if s not in terminals:
                            for c in reversed(s):
                                stack.append(c)
                        else:
                            stack.append(s) # terminalse direkt eklenir buna gerek duyduk cünkü id ters eklenirse kod patlar
                step += 1
            else:
                print("REJECTED") # action yoksa patla
                break

        elif current_state == current_input or current_state == EPSILON: #tabloda karsılık yoksa epsilon mu match mi
            stack.pop()
            if current_state != EPSILON: #match var ise
                input_tokens.pop(0)
            print(f"{step} | {''.join(stack)} | {''.join(input_tokens)} | Match and remove {current_state}")
            step += 1

        else: # tabloda karsılık yoksa patla
            print("REJECTED")
            break

        if ''.join(stack) == '$' and ''.join(input_tokens) == '$': #mutlu son
            print("ACCEPTED")
            break

def read_lr_table(file_name):
    with open(file_name) as f:
        lines = [line.strip().split(';') for line in f.readlines()]

    data = {}

    for line in lines[2:]: # 3. satırdan okumaya basla 
        if line[0].startswith('State'):
            state_data = {}
            for k, v in zip(lines[1][1:], line[1:]): #dict yapıyoruz key state value ise action/goto ve ona denk gelen islem
                if v.strip(): # hücre bos degilse kontrolu
                    state_data[k.strip()] = v.strip() # atamayı yap
            data[line[0].strip()] = state_data #state datayı asıl gonderecegimiz dataya aktarıyoz 
    return data

  
    
def process_lr(input_str, lr_table):
    stack = ['State_1'] #baslangıc state 1
    step = 0
    print('NO | STATE STACK | READ | INPUT | ACTION')

    while True:
        current_state = stack[-1] # input ve stackten gereken okumalar
        current_symbol = input_str[0]

        if current_symbol in lr_table[current_state]: #tabloda karısılık var mı
            action = lr_table[current_state][current_symbol] # actionı oku
            step += 1

            if 'State' in action: # action state e yonlendiriyorsa 
                state = action.split('_')[-1] # # hangi state oldugu extract ediliyo
                new_state = f'State_{state}' # o extract edilen state State stringine ekleniyo
                stack.append(new_state) # state stacke atılıyor
                input_str = input_str[1:] # okunan input cıkarılıyo artık
                print(f'{step} | {" ".join(stack)} | {current_symbol} | {input_str} | Shift to state {state}')
            elif '->' in action: #action kurala yonlendriyorsa 
                print(f'{step} | {" ".join(stack)} | {current_symbol} | {input_str} | Reverse {action}')
                production = action #actionu depoladık
                head, body = production.split('->') # oktan böldük
                body_len = len(body) #bodynin uzunluk aldık head kuralın ilk kısmı onu sonra kullancaz    
                stack = stack[:-body_len] # stackten uzunluk kadar cıkartılır. bunu yapma amacı ne kadar okuduk anlamak ve okunanı silmek

                if head in lr_table[stack[-1]]: # heade karsılık gelen durum var mı
                    goto_state = lr_table[stack[-1]][head].split('_')[-1] #tabledan onun durum numarası extract edilir
                    new_state = f'State_{goto_state}' # extract edilen numara state e eklenir
                    stack.append(new_state) # stacke artık yeni yaptıgımız state eklenir 
                else:
                    print('REJECTED') # tabloda yoksa patla
                    break
            elif action == 'Accept': #accept okunmus
                print(f'{step} | {" ".join(stack)} | {current_symbol} | {input_str} | {action}')
                print('ACCEPTED')
                break
        else: #tabloda karsılıgı yoksa patla
            print('REJECTED')
            break


def main():
    ll_table = read_ll_table(FILE_LL)
    lr_table = read_lr_table(FILE_LR)
    input_data = read_input_file(FILE_INPUT)

    print("Read LL(1) parsing table from file ll.txt.")
    print("Read LR(1) parsing table from file lr.txt.")
    print("Read input strings from file input.txt.")

    for data in input_data: #data okurken yapılması gereken işlemler boslukların atılması vs.
        table_type, input_str = data
        table_type = table_type.upper().strip()
        input_str = input_str.strip()
        
        if table_type == "LL": #ll okuduysak proces ll fonk cagırdık
            print(f"Processing input string {input_str} for LL(1) parsing table.")
            process_ll(input_str, ll_table)
        elif table_type == "LR": #lr okuduysak process lr fonk cagırdık
            print(f"Processing input string {input_str} for LR(1) parsing table.")
            process_lr(input_str, lr_table)
        else:
            print("Invalid table type")
        print()




if __name__ == "__main__":
    main()
