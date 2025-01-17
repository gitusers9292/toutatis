def advanced_lookup(username, sessionId):
    """
    Post request to retrieve obfuscated login info, enhanced to handle full phone numbers.
    """
    data = "signed_body=SIGNATURE." + quote_plus(dumps(
        {"q": username, "skip_recovery": "1"},
        separators=(",", ":")
    ))
    api = requests.post(
        'https://i.instagram.com/api/v1/users/lookup/',
        headers={
            "Accept-Language": "en-US",
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "Connection": "keep-alive",
            "Content-Length": str(len(data))
        },
        data=data,
        cookies={'sessionid': sessionId}
    )

    try:
        response = api.json()
        return {"user": response, "error": None}
    except decoder.JSONDecodeError:
        return {"user": None, "error": "Rate limit"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sessionid', help="Instagram session ID", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--username', help="One username")
    group.add_argument('-i', '--id', help="User ID")
    args = parser.parse_args()

    sessionId = args.sessionid
    search_type = "id" if args.id else "username"
    search = args.id or args.username

    infos = getInfo(search, sessionId, searchType=search_type)
    if not infos.get("user"):
        exit(infos["error"])

    infos = infos["user"]

    print(f"Informations about     : {infos['username']}")
    print(f"userID                 : {infos['userID']}")
    print(f"Full Name              : {infos['full_name']}")
    print(f"Verified               : {infos['is_verified']} | Is business Account : {infos['is_business']}")
    print(f"Is private Account     : {infos['is_private']}")
    print(f"Follower               : {infos['follower_count']} | Following : {infos['following_count']}")
    print(f"Number of posts        : {infos['media_count']}")
    if infos["external_url"]:
        print(f"External url           : {infos['external_url']}")
    print(f"IGTV posts             : {infos['total_igtv_videos']}")
    print(f"Biography              : {infos['biography']}")
    print(f"Linked WhatsApp        : {infos['is_whatsapp_linked']}")
    print(f"Memorial Account       : {infos['is_memorialized']}")
    print(f"New Instagram user     : {infos['is_new_to_instagram']}")

    # Handle public phone number and email
    if "public_email" in infos.keys() and infos["public_email"]:
        print(f"Public Email           : {infos['public_email']}")

    if "public_phone_number" in infos.keys() and infos["public_phone_number"]:
        phonenr = "+" + str(infos["public_phone_country_code"]) + " " + str(infos["public_phone_number"])
        try:
            pn = phonenumbers.parse(phonenr)
            country_code = region_code_for_country_code(pn.country_code)
            country = pycountry.countries.get(alpha_2=country_code)
            phonenr = f"{phonenr} ({country.name})"
        except phonenumbers.NumberParseException:
            pass
        print(f"Public Phone number    : {phonenr}")

    # Advanced lookup for obfuscated details
    other_infos = advanced_lookup(infos["username"], sessionId)
    if other_infos["error"] == "Rate limit":
        print("Rate limit, please wait a few minutes before trying again.")
    elif "message" in other_infos["user"].keys() and other_infos["user"]["message"] == "No users found":
        print("The lookup did not work on this account.")
    else:
        user_data = other_infos["user"]
        if "obfuscated_email" in user_data and user_data["obfuscated_email"]:
            print(f"Obfuscated email       : {user_data['obfuscated_email']}")
        else:
            print("No obfuscated email found.")

        if "obfuscated_phone" in user_data and user_data["obfuscated_phone"]:
            # Attempt to reconstruct the phone number using public phone data
            obfuscated_phone = user_data["obfuscated_phone"]
            if "public_phone_number" in infos:
                phonenr = "+" + str(infos["public_phone_country_code"]) + " " + obfuscated_phone
            else:
                phonenr = obfuscated_phone
            print(f"Obfuscated phone       : {phonenr}")
        else:
            print("No obfuscated phone found.")
    print("-" * 24)
    print(f"Profile Picture        : {infos['hd_profile_pic_url_info']['url']}")
