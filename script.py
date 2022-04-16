const Insta = require('node-insta-web-api/create')
const InstaClient = new Insta();
const readlineSync = require('readline-sync');
const moment = require('moment');
const colors = require("./lib/colors");
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const randstr = length =>
  new Promise((resolve, reject) => {
    var text = "";
    var possible =
      "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    for (var i = 0; i < length; i++)
      text += possible.charAt(Math.floor(Math.random() * possible.length));

    resolve(text);
  });

const genUniqueId = length =>
    new Promise((resolve, reject) => {
        var text = "";
        var possible =
            "1234567890";

        for (var i = 0; i < length; i++)
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        resolve(text);
    });

const generateIndoName = () => new Promise((resolve, reject) => {
    fetch('https://swappery.site/data.php?qty=1', {
        method:'GET'
    })
    .then(res => res.json())
    .then(res => {
        resolve(res)
    })
    .catch(err => {
        reject(err)
    })
});

const getSuggestionUsername = (headers, username, firstName) => new Promise((resolve, reject) => {
    const dataString = `email=${username}%40gmail.com&username=${username}&first_name=${firstName}&opt_into_one_tap=false`;
    fetch('https://www.instagram.com/accounts/web_create_ajax/attempt/', {
        method:'POST',
        headers,
        body: dataString
    })
    .then(res => res.json())
    .then(res => {
        resolve(res)
    })
    .catch(err => {
        reject(err)
    })
});


function getString(start, end, all) {
	const regex = new RegExp(`${start}(.*?)${end}`);
	const str = all
	const result = regex.exec(str);
	return result;
}

(async () => {
    try{
        const phoneNumber = '628324344444'; // isi dengan nomor yang ingin di pakai untuk daftar instagram
        const password = '43526#$#$67'; // isi dengan password akun instagram yang ingin di buat
        const imageLocation = 'images';
        const bioLocation = 'bio.txt';
        const targetFollow = 'webdev176' // isi dengan username ig yang ingin di follow menggunakan akun yang di buat pisahkan dengan , jika lebih dari 1
        console.log("");
        const indoName = await generateIndoName();
        const { result } = indoName;
        const name = result[0].firstname.toLowerCase()+result[0].lastname.toLowerCase()
        const uniqId = await genUniqueId(1);
        const username = name;
        console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,`mencoba buat akun dengan username ${username} dan password ${password}`,colors.Reset)

        //directory
        const folderYangMauDiUpload = imageLocation
        
        //joining path of directory
        const directoryPath = path.join(__dirname, folderYangMauDiUpload);
        const getPath = await  fs.readdirSync(directoryPath);
        const listPath = [];
        getPath.map(file => {
            listPath.push(file);

        })

        const imageName = listPath[Math.floor(Math.random() * listPath.length)];

        const bioFile = await fs.readFileSync(bioLocation, 'utf-8');
        const bioArray = bioFile.toString().split("\n");
        const bioFinal = bioArray[Math.floor(Math.random() * bioArray.length)];

        if (!username.includes("-")) {
            const headers = await InstaClient.getCookie();
            let suggestionName = await getSuggestionUsername(headers, username, result[0].firstname.toLowerCase());

            if(suggestionName.errors.hasOwnProperty('username')){
                console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,`username ${username} tidak tersedia, mencoba salah satu dari ${suggestionName.username_suggestions.join(',')}`,colors.Reset);
                suggestionName = {
                    ...suggestionName,
                    username: suggestionName.username_suggestions[Math.floor(Math.random() * suggestionName.username_suggestions.length)]
                }
            }else{
                console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,`username ${username} tersedia.`,colors.Reset)
                suggestionName = {
                    ...suggestionName,
                    username
                }
            }

            const theRealUsername = suggestionName.username;
            await InstaClient.registerLastAttemp(phoneNumber,theRealUsername,password,name);
            const sendOtp = await InstaClient.registerSendOtp(phoneNumber);
            if (sendOtp.sms_sent) {
                const otpCode = readlineSync.question('masukan kode otp : ');
                const resultRegister = await InstaClient.registerLastProcess(otpCode);
                if (resultRegister.account_created) {
                    console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                    `Akun berhasil dibuat dengan username ${theRealUsername} dan password ${password}`,
                    colors.Reset)
                    
                    fs.appendFileSync('./userpass.txt', `${theRealUsername}|${password}\n`, 'utf8')

                    console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                    `mencoba login dengan username ${theRealUsername} dan password ${password} untuk update bio`,
                    colors.Reset);
                    try{
                        await InstaClient.login(theRealUsername, password);
                        const payload = {
                            biography: bioFinal,
                            email: `${theRealUsername}`
                        }

                        const headersAfterLogin = await InstaClient.getHeaders();
                    
                        const resultUpdateBio = await InstaClient.updateProfile(payload);
                        if (resultUpdateBio.status && !resultUpdateBio.status == 'ok') {
                            console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgRed,
                            `gagal update bio untuk username ${theRealUsername}`,
                            colors.Reset);
                            console.log("");
                            console.log("");
                        }

                        console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                            `sukses update bio untuk username ${theRealUsername}`,
                            colors.Reset);

                        const photo = path.join(__dirname, `./${imageLocation}/${imageName}`);

                        console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                            `update profile picture untuk username ${theRealUsername}`,
                            colors.Reset);
                        const changeImageResult = await InstaClient.changeProfileImage(photo);

                        if(changeImageResult.changed_profile){
                            console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                            `sukses update profile pic`,
                            colors.Reset);

                            console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                            `Mencoba follow username ${targetFollow}`,
                            colors.Reset);

                            const follow = await InstaClient.followByUsername(targetFollow);
                            if (follow.status && follow.status == 'ok') {
                                console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgGreen,
                                `Sukses follow username ${targetFollow}`,
                                colors.Reset);

                            }else{
                                console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgRed,
                                `gagal follow username ${targetFollow}`,
                                colors.Reset);
                            }

                        }else{
                            console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgRed,
                            `sukses update profile pic`,
                            colors.Reset);
                        }
                        
                        
                    }catch(e){
                        console.log(e)
                        console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgRed,
                    `ada masalah : ${e}`,
                    colors.Reset);
                    console.log("");
                    console.log("");
                    }

                }else{
                    console.log(`[ ${moment().format("HH:mm:ss")} ] `,colors.FgRed,
                    `Akun gagal dibuat.`,
                    colors.Reset)
                    console.log(resultRegister)
                    console.log("");
                    console.log("");
                    
                }
            }else{
                console.log('Failed Send Otp.');
                console.log("");
                console.log("");
            }
        }else{
            console.log(
                "[" +
                " " +
                moment().format("HH:mm:ss") +
                " " +
                "]" +
                " " +
                "=>" +
                " " +
                colors.FgRed,
                "Message : username include character not allowed for register",
                colors.Reset
            );
            console.log("");
            console.log("");
        }
    }catch(e){
        console.log(e)
    }
})();