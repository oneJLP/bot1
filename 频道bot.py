import qq
from config import appid, token
import base64
import json
import random
import logging


logging.basicConfig(level=logging.INFO)


def setting(mode: object, sd: object = None) -> object:
    with open('songsAndDifficulty.json', 'r', encoding='utf8') as f:
        songsAndDifficulty1 = json.loads(f.read())
    if not mode:
        return songsAndDifficulty1
    elif mode == 1:
        k1 = '???'
        for k, v in setting(0).items():
            if sd[0] in k.replace(' ', '_') or sd[0] in k.lower().replace(' ', '_'):
                songsAndDifficulty1[k] = sd[1]
                k1 = k
                break
        with open('songsAndDifficulty.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(songsAndDifficulty1))
            f.close()
        return k1
    elif mode == 2:
        songsAndDifficulty1[sd[0]] = sd[1]
        with open('songsAndDifficulty.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(songsAndDifficulty1))
            f.close()


songsAndDifficulty = setting(0)


def testify(test):
    if test <= 14.2:
        package = '本次考试曲目为' + random.choice(['Class memory', 'Chronologika', 'GOODTEK', '风屿 IN']) + '全连\n加油，相信你一定可以的喵~'
    else:
        package = '以下三首曲目中，需要任意一首曲目rks大于等于13.9\n'
        useable = []
        for k, v in songsAndDifficulty.items():
            if test <= v <= test + 0.3:
                useable.append(k)
        random.shuffle(useable)
        for song in useable[:3]:
            package += '<' + song + '>定数为' + str(songsAndDifficulty[song]) + '，acc达到' + str(
                round((13.9 / songsAndDifficulty[song]) ** 0.5 * 45 + 55, 2)) + '%即可过关' + '\n'
        package += '加油，相信你一定可以的喵~'
    return package


def get_testified_list(mode: int, uid: str = '', buid='', msg=None):
    with open('testified_list.json', 'r', encoding='utf8') as f:
        testified_list1 = json.loads(f.read())
    if mode == 0:
        return testified_list1
    elif mode == 1:
        testified_list1[uid] = [buid, '']
        with open('testified_list.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(testified_list1))
            f.close()
    elif mode == 2:
        del testified_list1[uid]
        with open('testified_list.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(testified_list1))
            f.close()
    elif mode == 3:
        testified_list1[uid] = [testified_list1[uid][0], msg]
        with open('testified_list.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(testified_list1))
            f.close()


def get_allowed_list(mode: int, buid: str = ''):
    with open('allowed_list.json', 'r', encoding='utf8') as f:
        allowed_list1 = json.loads(f.read())
    if mode == 0:
        return allowed_list1
    elif mode == 1:
        allowed_list1.append(buid)
        allowed_list1 = list(set(allowed_list1))
        with open('allowed_list.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(allowed_list1))
            f.close()
    elif mode == 2:
        allowed_list1.remove(buid)
        with open('allowed_list.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(allowed_list1))
            f.close()


def f(x):
    return x != ''


client = qq.Client()


@client.event
async def on_message(message: qq.Message):
    # print(message.guild.roles)
    global member, roles
    msg = message.content.replace('<@!2723538054056343035>', '').strip()
    uname = message.author.name
    uid = str(message.author.id)
    print(msg, uname)
    try:
        member = await message.guild.fetch_member(message.author.id)
        roles = [x.name for x in member.roles]
    except AttributeError:
        pass
    attachment_urls = [x.url for x in (message.attachments if message.attachments else [])]

    isadmin = '频道主' in roles or '超级管理员' in roles
    mention = list(filter(f, [x if not x.bot else '' for x in message.mentions]))
    if mention == []:
        mention = None
    else:
        mention = await message.guild.fetch_member(mention[0].id)
    # print(message.channel.get_partial_message(message.id))
    if not uname == 'Satellite-测试中':
        if msg == '/ping':
            await message.channel.send('当前频道服务在线', mention_author=member)
        elif msg == '/help':
            await message.channel.send('请见#使用须知', mention_author=member)
        elif msg[:6] in ('/查询定数 ', '/获取定数 '):
            txt = '包含“' + msg[6:] + '”' + '的曲目及其定数如下：'
            for k, v in setting(0).items():
                if msg[6:] in k.replace(' ', '_') or msg[6:] in k.lower().replace(' ', '_'):
                    txt += ('\n' + k + '定数为: ' + str(v))
            await message.channel.send(txt)
        elif msg[:6] == '/test ':
            if uid in get_testified_list(0).keys():
                await message.channel.send('你已经获取过一次审核题目了，请勿重复获取！特殊情况请向管理员申请清除记录', mention_author=member)
            else:
                try:

                    rks = float(msg.split()[1])
                    if rks < 13.5:
                        await message.channel.send('rks太低啦，练练再来审核哦！（至低需要13.5）', mention_author=member)
                    else:
                        get_testified_list(1, uid, msg.split()[2].replace('UID:', ''))
                        await message.channel.send('欢迎>' + uname + '<前来审核！\n' + testify(rks) + (
                            '\n你的一次获取考题机会已耗尽，无法再次获取\n\n打完歌之后请使用/upload命令上传你的消息记录截图和结算截图！' if not isadmin else ''),
                                                   mention_author=member)

                        await member.add_roles(message.guild.get_role(15454880))

                except Exception as e:
                    print(e)
                    await message.channel.send('输入格式出现错误！应当为：/test 你的rks 你的b站UID', mention_author=member)
        elif msg == '/待审队列':
            if isadmin:
                待审list = {}
                i = 1
                for k, v in get_testified_list(0).items():
                    if v[1] != '':
                        待审list[str(i) + '：' + k + '：\n审核内容：'] = json.loads(v[1])
                        i += 1
                await message.channel.send('待审队列如下：', mention_author=member)
                for k, v in 待审list.items():
                    await message.channel.send(k)
                    for i in v:
                        await message.channel.send(image=i)

            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg == '/已取题':
            if isadmin:
                await message.channel.send('已取题群员如下：\n' + '\n'.join(
                    [k + ('：未完成' if v[1] == '' else '：待审中')
                     for k, v in get_testified_list(0).items()]).replace('\n\n', '\n'))
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg[:7] == '/upload':
            try:
                if len(attachment_urls) < 2:
                    await message.channel.send('你需要上传至少两张图片(包括一张消息记录截图和一张打歌结算截图)，上传失败！', mention_author=member)
                else:
                    get_testified_list(3, uid, msg=json.dumps(attachment_urls))
                    await message.channel.send('审核内容上传成功！', mention_author=member)
                    await member.add_roles(message.guild.get_role(15454891))
                    await member.remove_roles(message.guild.get_role(15454880))
            except Exception as e:
                print(e)
                await message.channel.send('你还没有使用/test命令获取审核题目！', mention_author=member)
        elif msg[:5] == '/get ':
            if isadmin:
                await message.channel.send('已发送', mention_author=member)
                await message.author.send(base64.b64encode(msg[5:].encode('utf-8')).decode('ascii') + '''\n这是你的入群密码
进群请修改昵称为昵称+B站uid
不改还是会被踢
大群群号730173176''')
                get_allowed_list(1, msg[5:])
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg[:7] == '/allow ':
            if isadmin:
                try:
                    await mention.send(base64.b64encode(msg.split(' ')[-1].encode('utf-8')).decode('ascii') + '''\n这是你的入群密码(如果有等号，等号也是密码的一部分)
请根据此密码及时进群！密码过期概不负责
进群请修改昵称为昵称+B站uid
不改还是会被踢
大群群号730173176''')
                    await message.channel.send('密码已发送，若未收到请请求审核员再次通过', mention_author=mention)

                    if uid in list(get_testified_list(0).keys()):
                        get_testified_list(2, str(mention.id))
                    get_allowed_list(1, msg.split(' ')[-1])
                    await mention.add_roles(message.guild.get_role(15454914))
                    await mention.remove_roles(message.guild.get_role(15454891))
                except Exception as e:
                    print(e)
                    await message.channel.send('输入格式出现错误或该群员不存在！\n'+str(repr(e)), mention_author=member)
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg[:8] == '/allow1 ':
            if isadmin:
                待审list1 = [(k, v[0]) if v[1] != '' else '' for k, v in get_testified_list(0).items()]
                待审list1 = list(filter(f, 待审list1))
                print(待审list1)
                try:
                    if msg[8:] == 'all':
                        sd1 = 待审list1.copy()
                    else:
                        sd1 = [待审list1[int(msg[8:]) - 1]]
                    for sd in sd1:
                        print(sd)
                        m = await message.guild.fetch_member(sd[0])
                        await m.send(base64.b64encode(sd[1].encode('utf-8')).decode('ascii') + '''\n这是你的入群密码(如果有等号，等号也是密码的一部分)
请根据此密码及时进群！密码过期概不负责
进群请修改昵称为昵称+B站uid
不改还是会被踢
大群群号730173176''')
                        await message.channel.send('密码已发送，若未收到请请求审核员再次通过', mention_author=m)
                        get_testified_list(2, sd[0])
                        get_allowed_list(1, sd[1])
                        await m.add_roles(message.guild.get_role(15454914))
                        await m.remove_roles(message.guild.get_role(15454891))
                except Exception as e:
                    print(e)
                    await message.channel.send('输入格式出现错误或该序号不存在！\n'+str(repr(e)), mention_author=member)
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg[:11] == '/disallow1 ':
            if isadmin:
                待审list1 = [(k, v[0]) if v[1] != '' else '' for k, v in get_testified_list(0).items()]
                待审list1 = list(filter(f, 待审list1))
                try:
                    disallow1_uid = 待审list1[int(msg[11:]) - 1][0]
                    m = await message.guild.fetch_member(disallow1_uid)
                    get_testified_list(3, disallow1_uid, msg='')
                    await message.channel.send('你的审核内容不合格，没有通过审核', mention_author=m)
                    await m.add_roles(message.guild.get_role(15454880))
                    await m.remove_roles(message.guild.get_role(15454891))
                except Exception as e:
                    print(e)
                    await message.channel.send('输入格式出现错误或该序号不存在！\n'+str(repr(e)), mention_author=member)
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        elif msg == '/withdraw':
            try:
                await message.channel.send('你的审核内容已撤销！', mention_author=member)
                get_testified_list(3, uid, msg='')
            except:
                await message.channel.send('你还没有使用/test命令获取审核题目或还没有上传审核内容！', mention_author=member)
        elif msg[:5] == '/cal ':
            try:
                l = msg.split()

                await message.channel.send('您这首曲的rks为:' + str(
                    round(float(l[2]) * ((float(l[1]) * 100 - 55) / 45) ** 2, 2)), mention_author=member)
            except:
                await message.channel.send('输入格式出现错误！', mention_author=member)
        elif msg[:4] == '/定数 ':
            try:
                a = msg.split()[1]
                await message.channel.send('定数为' + a + '的曲目：\n' + '\n'.join(
                    sorted(k if v == float(a) else '' for k, v in songsAndDifficulty.items())[::-1]).rstrip(),
                                           mention_author=member)
            except:
                await message.channel.send('输入格式出现错误！', mention_author=member)
        elif msg[:5] == '/清除记录':
            if isadmin:
                await mention.remove_roles(message.guild.get_role(15454880))
                try:
                    get_testified_list(2, str(mention.id))
                    await message.channel.send('你的记录已被清除，可以重新获取审核题目', mention_author=mention)

                except:
                    await message.channel.send('输入格式出现错误或该群员不存在！', mention_author=member)
            else:
                await message.channel.send('你的权限不足！', mention_author=member)
        else:
            await message.channel.send('未知的命令：'+msg.split(' ')[0], mention_author=member)


@client.event
async def on_ready():
    print('登录成功')


if __name__ == '__main__':
    client.run(token=appid + '.' + token)
