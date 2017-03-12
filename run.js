const { Wechaty, Message, Contact } = require('wechaty');
const util = require('util');

Wechaty.instance()
  .on('scan', (url, code) => console.log(`Scan QR code to login: ${code}\n${url}`))
  .on('login', user => console.log(`user: ${user} login successfully`))
  .on('message', message => {
    console.log(util.inspect(message));
    //原对象回复
    message.from().say('just for test');
    let replyMsg = new Message();
    replyMsg.to('filehelper');
    replyMsg.content('shit for test');
    this.send(replyMsg);
  })
  .on('logout', user => console.log(`user: ${user} logout...`))
  .init()
  .then(res => {
    if (res) console.log(res);
  }, err => {
    console.error(err);
  });