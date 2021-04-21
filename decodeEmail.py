import email.parser
import os
import sys

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def removespecialspace(src) -> str:
    import re
    # this regex will replace all special characters with a space
    return re.sub('\W+',' ',src).strip()

def removehtmltag(src) -> str:
    import re
    html_tag = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    return re.sub(html_tag,"", src.replace("\n","NEXTLINEPLACEHOLDER")).replace("=0A","").replace("=0D","").replace("=3D","=").replace("=09","").replace("=20","").replace("=","").replace("&","").replace("nbsp"," ").replace("NEXTLINEPLACEHOLDER","\n")

def removecsstag(src) -> str:
    import re
    import time
    #     css_tag = re.compile("#.+;}")
    #     return re.sub(css_tag,"",src)
    start_time = int(time.time())
    print("removecss starts run!")
    comment = re.compile("/\*[\w ]+\*/")
    cssproperties = re.compile("(?<={)[\w;\n \t\-/*?.\"\',():%#!]*?(?=})")
    cssselector = re.compile("(.*[ \n]*){1,2}{}")
    answer = re.sub(comment,"",re.sub(cssselector,"", re.sub(cssproperties,"",src))).replace("{","").replace("}","")
    end_time = int(time.time())
    print("It takes %d seconds to remove css in this file" %(end_time-start_time))
    return answer
#     return re.sub(cssselector,"",re.sub(comment,"", re.sub(cssproperties,"",removenoise)))
#     return re.sub(comment,"",removenoise)
#     return src




def base64decode(src) -> str:
    import base64
    result = src.replace("NEXTLINEPLACEHOLDER","")  # remove all next-line inside b64-encoded content
    #     trim = re.compile("[a-zA-Z0-9\+\/]*") ##replaced by NEXTLINEPLACEHOLDER
    #     result = trim.findall(result)
    #     print(result)
    try:
        result = base64.b64decode(result).decode("utf-8")
        print("decode_success1")
        if len(result) < 0.5*len(src.replace("NEXTLINEPLACEHOLDER","")):
            print("unexpectedly short %f" %(len(result)/len(src.replace("NEXTLINEPLACEHOLDER",""))))
            return src
    except base64.binascii.Error:
        try:
            result = base64.b64decode(result[:-(len(result)%4)]).decode("utf-8")
            print("decode_success2")
            if len(result) < 0.5*len(src.replace("NEXTLINEPLACEHOLDER","")):
                print("unexpectedly short%f" %(len(result)/len(src.replace("NEXTLINEPLACEHOLDER",""))))
                return src
        except base64.binascii.Error:
            print("decode_failed1")
            return src
    except UnicodeDecodeError:
        print("decode_failed2")
        return src
    return result

def findb64decode(src) -> str:
    import re
    b64_head = re.compile("(?P<Head>-{4}[a-zA-Z0-9]{10,})(?P<Content>NEXTLINEPLACEHOLDERContent.*Content-Transfer-Encoding: base64)(.*)(?P=Head)")
    result = src.replace("\n","NEXTLINEPLACEHOLDER")
    match = b64_head.findall(result)
    #     if not match:
    #         print("no match")
    for capture_group in match:
        header = capture_group[0]
        original_content = base64decode(capture_group[2])
        result = result.replace(capture_group[0],"").replace(capture_group[1],"").replace(capture_group[2], original_content)
    return result.replace("NEXTLINEPLACEHOLDER","\n")

def removeheader(src) -> str:
    import re
    src = src.replace("\n","NEXTLINEPLACEHOLDER")
    header = re.compile("From .*@.*Return-Path.*X-Keywords:.*?NEXTLINEPLACEHOLDER")
    quotedprintable = re.compile("-{4}[a-zA-Z0-9]{10,}.*?Encoding: quoted-printableNEXTLINEPLACEHOLDER")
    result = re.sub(header,"",src)
    result = re.sub(quotedprintable,"",result)
    return result.replace("NEXTLINEPLACEHOLDER","\n")

def recursivePayloadSearch(message) -> str:
    if isinstance(message._payload,list): #payload is a list of message
        string = ""
        for i in message._payload:
            string += recursivePayloadSearch(i)
            string += "\n////////////////////////////////////////\n"
        return string
    else: #payload is a message
        if message.get_content_type() == "image/gif":
            payload = "THIS-IS-IMAGE"
            return payload
        else:
            payload = message._payload
            payload = findb64decode(payload)
            #             payload = removehtmltag(payload)
            #             payload = removecsstag(payload)
            payload = removeheader(payload)
            return payload

def decodeSubject(message) -> str:
    import re
    import traceback
    import urllib.parse as p
    import base64
    b64prefix = re.compile("=\?[uUtTfF]{3}-8\?[a-zA-Z]\?(.*)\?=")
    win1252prefix = re.compile("=\?[WwIiNnDdOoWwSs]{7}-[0-9]{4}\?[a-zA-Z]\?(.*){1}\?=")
    iso8859prefix = re.compile("=\?[iIsSoO]{3}-8859-[0-9]{1,}\?[a-zA-Z]\?(.*){1}\?=")
    usasciiprefix = re.compile("=\?[uUsS]{2}-[asciASCI]{5}\?[a-zA-Z]\?(.*){1}\?=")
    subject = ""
    for header in message.items():
        if header[0] == "Subject":
            subject = header[1].replace("?==?","?=\n=?")
            unwrappedb64 = b64prefix.findall(subject)
            unwrappedwin1252 = win1252prefix.findall(subject)
            unwrappediso8859 = iso8859prefix.findall(subject)
            unwrappedusascii = usasciiprefix.findall(subject)
            if unwrappedb64:
                subject = "".join(unwrappedb64).replace("_"," ")
                try:
                    temp = subject
                    temp = base64.b64decode(subject).decode("utf-8")
                    if len(temp) > 0.1*len(subject):
                        subject = temp
                except base64.binascii.Error:
                    try:
                        temp = base64.b64decode(subject[:-(len(subject)%4)]).decode("utf-8")
                        if len(temp) > 0.1*len(subject):
                            subject = temp
                    except base64.binascii.Error:
                        print("temp = %s" %temp)
                        traceback.print_exc()
                    except UnicodeDecodeError:
                        pass
                except UnicodeDecodeError:
                    pass
            elif unwrappedwin1252:
                subject = "".join(unwrappedwin1252)
                subject = subject.replace("=91", "\'").replace("=92", "\'").replace("_"," ").replace("=93","\"").replace("=94","\"").replace("=96","-").replace("=B9","¹")
            elif unwrappediso8859:
                subject = "".join(unwrappediso8859)
                subject = subject.replace("=A0", " ")
            elif unwrappedusascii:
                subject = "".join(unwrappedusascii)
            subject = p.unquote(subject.replace("=", "%"))
    return subject

def pure_b64decode(src) -> str:
    result = base64decode(src.replace("\n","NEXTLINEPLACEHOLDER"))
    if src == result:
        return "failed"
    return result.replace("NEXTLINEPLACEHOLDER","\n")




def oriParser(input_txt):
    import traceback
    parser = email.parser.Parser()
    
    EmailMessage = parser.parsestr(input_txt, headersonly = False)
    # subject = ""
    content = ""

    # try:
    #     subject = decodeSubject(EmailMessage)
    # except Exception:
    #     # traceback.print_exc()
    #     print("Get Subject Error: %s" %(file_id))
    try:
        content = recursivePayloadSearch(EmailMessage)
    #                 content = removehtmltag(removecsstag(content))
    except Exception:
        print("Get Content Error: %s" %(input_txt))

    try:
        #                 blockPrint()
        trypayload = EmailMessage._payload
        pure_b64 = pure_b64decode(trypayload)
        if len(pure_b64)>0.6*len(EmailMessage._payload):
            #                     enablePrint()
            print(input_txt)
            content = pure_b64
    #                 enablePrint()
    except Exception:
        pass
    #                 enablePrint()
    content = removehtmltag(content)
    if content.find("{") != -1:
        print("has {}")
        content = removecsstag(content)
    content = removespecialspace(content).replace("\n","").replace(",","")
    # subject = subject.replace("\n","").replace(",","")
    return content

def findUrl(path):
    import traceback
    parser = email.parser.Parser()

    try:
        file_pointer = open(path, "r", encoding = "utf-8", errors="ignore")
    except FileNotFoundError:
        print("No such file")
    EmailMessage = parser.parse(file_pointer, headersonly = False)
    content = ""

    try:
        content = recursivePayloadSearch(EmailMessage)
    #                 content = removehtmltag(removecsstag(content))
    except Exception:
        print("Get Content Error: %s" %(path))

    try:
        #                 blockPrint()
        trypayload = EmailMessage._payload
        pure_b64 = pure_b64decode(trypayload)
        if len(pure_b64)>0.6*len(EmailMessage._payload):
            # print(path)
            content = pure_b64
    except Exception:
        pass
    return content
