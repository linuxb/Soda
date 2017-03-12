# -*-encoding:utf-8-*-
import os
import itchat
import re
import shutil
import time
import traceback
from itchat.content import *

msg_dict = {}

def fmt(s):
  if int(s) < 10:
    return "0" + s
  return s

# 清理过期的消息缓存
def cleanup_message():
  if msg_dict.__len__ > 0:
    for msgId in list(msg_dict):
      if time.time() - msg_dict.get(msgId, None)['msg_time'] > 130.0:
        item = msg_dict.pop(msgId)
        # 删除缓存文件
        if item['msg_type'] == 'Picture':
          print ("cleanup file: %s" % item['msg_content'])
          os.remove(item['msg_content'])

# 将接收到的信息保存进字典
@itchat.msg_register([TEXT, SHARING, PICTURE], isFriendChat=True, isGroupChat=True)
def save_message(msg):
  print ("received message: %s" % msg["Content"])
  # 获取消息的接受时间
  current_time = time.localtime()

  format_time = current_time.tm_year.__str__() \
                      + "/" + current_time.tm_mon.__str__() \
                      + "/" + current_time.tm_mday.__str__() \
                      + " " + fmt(current_time.tm_hour.__str__()) \
                      + ":" + fmt(current_time.tm_min.__str__()) \
                      + ":" + fmt(current_time.tm_sec.__str__())
  
  msg_id = msg["MsgId"]
  # !fix 群聊情景如果有陌生人发送信息
  # 群聊中的UserName就是这个群，自动回复回复到群里
  msg_from = None
  if itchat.search_friends(userName=msg['FromUserName']) != None:
    msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
  else: 
    msg_from = u"群里的某位伙伴" 
  msg_from_id = msg['FromUserName']
  msg_type = msg['Type']
  msg_time = msg['CreateTime']
  msg_content = None
  msg_url = None

  if msg['Type'] == 'Text':
    msg_content = msg['Text']
  elif msg['Type'] == 'Picture':
    # 获取图片的缓存目录
    msg_content = msg['FileName']
    # 下载
    msg['Text'](msg['FileName'])
  elif msg['Type'] == 'Sharing':
    msg_content = msg['Text']
    msg_url = msg['Url']
  # 保存到字典, 以ID为索引
  msg_dict.update({
    msg_id: {
      "msg_from": msg_from,
      "msg_time": msg_time,
      "msg_content": msg_content,
      "msg_url": msg_url,
      "msg_type": msg_type,
      "format_time": format_time,
      "msg_from_id": msg_from_id
    }
  })

  #cleanup
  cleanup_message()

# 判断是不是撤回操作，接收到note类的通知
@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True)
def resume_message(msg):
  print ("%s" % msg["Content"])
  # 图片等资源的缓存目录
  if not os.path.exists("./cache/"):
    os.mkdir("./cache/")
  # 检测是否有撤回标记
  if re.search(u"\<replacemsg\>\<\!\[CDATA\[.*撤回了一条消息\]\]\>\<\/replacemsg\>", msg["Content"]) != None:
    # 获取消息的ID
    old_msg_id = re.search(r"\<msgid\>(.*?)\<\/msgid\>", msg["Content"]).group(1)
    # 根据id查字典
    old_msg = msg_dict.get(old_msg_id, {})
    # 将撤回信息发送到文件助手
    msg_holy = u"呵呵," \
      + old_msg.get('msg_from', None) \
      + u"在[" + old_msg.get('format_time') \
      + u"]撤回了消息，内容为: " \
      + old_msg.get('msg_content', None)
    try:
      if old_msg['msg_type'] == 'Sharing':
        msg_holy += u" ,是这个不可告人的链接哦: " + old_msg.get('msg_url', None)
        itchat.send(msg_holy, toUserName=old_msg['msg_from_id'])
      elif old_msg['msg_type'] == 'Picture':
        msg_holy += u" ,她发的见不得光的图片已被B哥AI自动保存: "
        # 发送回去
        itchat.send(u'撤回图片没用的', toUserName=old_msg['msg_from_id'])
        itchat.send_image(old_msg['msg_content'], toUserName=old_msg['msg_from_id'])
        shutil.move(old_msg['msg_content'], r"./cache/")
      elif old_msg['msg_type'] == 'Text':
        reply_msg = u"呵呵，撤回没用" + old_msg['msg_content']
        itchat.send(reply_msg, toUserName=old_msg['msg_from_id'])      
      itchat.send(msg_holy, toUserName="filehelper")
    except:
      traceback.print_exc()
      # 退出登陆
      itchat.logout()
  cleanup_message()

itchat.auto_login()
itchat.run()