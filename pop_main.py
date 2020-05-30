import socket
import ssl
import argparse
import os
import base64
import re
import itertools


CRLF = "\r\n"

host_dict = {
            "mail": ('pop.mail.ru', 995),
            "yandex": ('pop.yandex.ru', 995),
            "rambler": ('pop.rambler.ru', 995)
}


def read_letter(sock):
    buff = bytes()
    while True:
        data = sock.recv(512)
        buff += data
        if data.endswith("{}".format(CRLF).encode('utf-8')):
            break
    return buff


def request(socket, request):
    socket.send((request + CRLF).encode())
    recv_data = read_letter(socket)
    recv_data = recv_data.decode()
    return recv_data


def work(args, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = ssl.wrap_socket(client)
    client.connect((host, port))
    res = client.recv(1024)
    print(res)
    res = request(client, 'USER '+args.email[0])
    print(res)
    res = request(client, 'PASS '+args.password[0])
    print(res)
    if args.top and args.all_text:
        print("parameters all and top should be used separately")
    else:
        req = 'RETR ' + str(args.number[0])
        res = request(client, req)
        print(res)
        res = request(client, 'QUIT')
        if args.from_h:
            print(get_from(res))
        if args.to_h:
            print(get_to(res))
        if args.subject:
            s = get_subject(res)
            if not s:
                print('Subject: no subject')
            else:
                print(s)
        if args.date:
            print(get_date(res))
        if args.all_text or args.all_message:
            print(find_text(res))
        if args.top:
            print(find_text(res)[0:args.top[0]])
        if args.all_message:
            download_attach(res)

def get_host_name(email):
    host_getter = re.compile(r'\.(.+?)@')
    mo = re.search(host_getter, email[::-1])
    if mo:
        return mo.group(1)[::-1]

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        default=argparse.SUPPRESS,
                        help='show this message and quit')
    parser.add_argument(nargs=1, type=str, dest='email', help='users email')
    parser.add_argument(nargs=1, type=str, dest='password', help='users password')
    parser.add_argument(nargs=1, type=int, dest='number', help='letter number from last to oldest')
    parser.add_argument('-top', nargs=1, type=int, help="get certain number of SYMBOLS from letter's text")
    parser.add_argument('-all_message', action='store_true', help='get text and download attachments')
    parser.add_argument('-all_text', action='store_true', help='get message text without attachments')
    parser.add_argument('-from_h', action='store_true', help='get header from')
    parser.add_argument('-to_h', action='store_true', help='get header to')
    parser.add_argument('-subject', action='store_true', help='get header subject')
    parser.add_argument('-date', action='store_true', help='get header date')
    args = parser.parse_args()
    name = get_host_name(args.email[0])
    if name:
        try:
            host, port = host_dict[name]
        except KeyError:
            print("unknown host. please enter valid email in email parameter")
        else:
            work(args, host, port)
    else:
        print("unknown host. please enter valid email in email parameter")

def filter_parts(part):
    return "Content-Transfer-Encoding: base64" in part


def get_content_parts(letter):
    bound = re.compile(r'boundary="(.+)"')
    mo_list = re.findall(bound, letter)
    splitter = r"|".join(mo_list)
    parts = re.split(splitter, letter)
    f_parts = filter(filter_parts, parts)
    return list(f_parts)


def download_attach(letter):
    parts = get_content_parts(letter)
    attach = filter(lambda s: "Content-Type: text/plain" not in s
                  and "Content-Type: text/html" not in s, parts)
    attach = list(attach)
    for at in attach:
        sp = list(filter(lambda s: s != "", at.split("\r\n")))
        sp = list(sp)
        rez = sp[3:len(sp) - 1]
        j = "".join(rez)
        data = base64.b64decode(j.encode('utf-8'))
        name = re.compile(r'name="=\?UTF-8\?B\?(.+)\?=')
        simple_name = re.compile(r'name="(.+)"')
        name_res = re.search(name, at)
        if name_res:
            dec = base64.b64decode(name_res.group(1)).decode('utf-8')
            print(dec)
            read_attach(data, dec)
        else:
            simple_name_res = re.search(simple_name, at)
            if simple_name_res:
                r = simple_name_res.group(1)
                print(r)
                read_attach(data, r)


def read_attach(attach_file_data, file_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    attach_file_path = os.path.join(current_path, file_name)
    with open(attach_file_path, 'wb') as f:
        f.write(attach_file_data)
    print('attached file is saved ' + attach_file_path)


def find_text(letter):
    parts = get_content_parts(letter)
    text = filter(lambda s: "Content-Type: text/plain" in s, parts)
    for t in text:
        sp = list(filter(lambda s: s != "", t.split("\r\n")))
        sp = list(sp)
        rez = sp[2:len(sp)-1]
        d = []
        for o in rez:
            d.append(base64.b64decode(o))
        j = b"".join(d)
        return j.decode('utf-8')


def next_subject_line(line):
    return line.startswith(" ") or line.startswith('Subject: ')

def get_64(line):
    line_h = re.compile(r' =\?UTF-8\?B\?(.+)\?=')
    mo = re.search(line_h, line)
    if mo:
        slice_p = mo.group(1)
        return base64.b64decode(slice_p).decode("utf-8")
    return ""

def get_from(letter):
    simple_from = re.compile(r'From: (.+)')
    from_h = re.compile(r'From: =\?UTF-8\?B\?(.+)\?=(.+)')
    fr = re.search(from_h, letter)
    if fr:
        name = fr.group(1)
        name_str = base64.b64decode(name).decode("utf-8")
        return "From: {} ".format(name_str)+fr.group(2)
    else:
        fr = re.search(simple_from, letter)
        if fr:
            return "From: "+fr.group(0)
        else:
            return


def get_to(letter):
    simple_to = re.compile(r'To: (.+)')
    to_h = re.compile(r'To: =\?UTF-8\?B\?(.+)\?=(.+)')
    to_p = re.search(to_h, letter)
    if to_p:
        name = to_p.group(1)
        name_str = base64.b64decode(name).decode("utf-8")
        return "To: {} ".format(name_str)+to_p.group(2)
    else:
        fr = re.search(simple_to, letter)
        if fr:
            return "To: "+fr.group(0)
        else:
            return

def get_date(letter):
    date_h = re.compile(r'Date: (.+)')
    date = re.search(date_h, letter)
    return date.group(0)

def get_subject(letter):
    subject_h = re.compile(r'Subject: =\?UTF-8\?B\?(.+)\?=(.+)')
    subject = re.search(subject_h, letter)
    if subject:
        after_subject = letter[subject.start():]
        lines = after_subject.split('\n')
        f_lines = itertools.takewhile(next_subject_line, lines)
        map_lines = map(get_64, f_lines)
        return "Subject: "+"".join(map_lines)

def find_headers(letter):
    print(get_to(letter))
    print(get_from(letter))
    print(get_date(letter))
    print(get_subject(letter))


if __name__ == '__main__':
    main()