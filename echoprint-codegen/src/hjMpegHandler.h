//
//  Mpeg Handler by hjwon
//  Copyright 2012 Soribada. All rights reserved.
//


#ifndef HJMPEGHANDLER_H
#define HJMPEGHANDLER_H

//#include <memory.h>

#define USE_LAYER_1
#define USE_LAYER_2

/*
* Please check this and don't kill me if there's a bug
* This is a (nearly?) complete header analysis for a MPEG-1/2/2.5 Layer I, II or III
* data stream
*/

int is_syncword_mp123(const void *const headerptr)
{
	const unsigned char *const p = (unsigned char *)headerptr;
	static const char abl2[16] =
		{ 0, 7, 7, 7, 0, 7, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8 };

	if ((p[0] & 0xFF) != 0xFF)
		return 0;       /* first 8 bits must be '1' */
	if ((p[1] & 0xE0) != 0xE0)
		return 0;       /* next 3 bits are also */
	if ((p[1] & 0x18) == 0x08)
		return 0;       /* no MPEG-1, -2 or -2.5 */
	if ((p[1] & 0x06) == 0x00)
		return 0;       /* no Layer I, II and III */
#ifndef USE_LAYER_1
	if ((p[1] & 0x06) == 0x03*2)
		return 0; /* layer1 is not supported */
#endif
#ifndef USE_LAYER_2
	if ((p[1] & 0x06) == 0x02*2)
		return 0; /* layer1 is not supported */
#endif
	if ((p[2] & 0xF0) == 0xF0)
		return 0;       /* bad bitrate */
	if ((p[2] & 0x0C) == 0x0C)
		return 0;       /* no sample frequency with (32,44.1,48)/(1,2,4)     */
	if ((p[1] & 0x18) == 0x18 && (p[1] & 0x06) == 0x04
		&& abl2[p[2] >> 4] & (1 << (p[3] >> 6)))
		return 0;
	if ((p[3] & 3) == 2)
		return 0;       /* reserved enphasis mode */
	return 1;
}

bool GetMpegRegion(unsigned char * lpMpegData, unsigned long dwLength, unsigned long& dwStartPos, unsigned long& dwEndPos)
{
	bool bReturn = false;
	unsigned char * buf = lpMpegData;

	dwStartPos = 0;
	dwEndPos = dwLength;

	// check ID3 TAG v2
	if (buf[0] == 'I' && buf[1] == 'D' && buf[2] == '3') {
		buf += 4;
		buf[2] &= 127; buf[3] &= 127; buf[4] &= 127; buf[5] &= 127;
		int len = (((((buf[2] << 7) + buf[3]) << 7) + buf[4]) << 7) + buf[5];
		buf += len;
	}

	int aid_header = (memcmp(buf, "AiD\1", 4) == 0);
	if (aid_header)
	{
		buf += 2;
		aid_header = (unsigned char) buf[0] + 256 * (unsigned char) buf[1];
		/* skip rest of AID, except for 6 bytes we have already read */
		buf += (aid_header - 6);

		/* read 4 more bytes to set up buffer for MP3 header check */
		buf += 4;
	}

	/* look for valid 8 byte MPEG header  */
	unsigned char * bufTmp = 0;
	while(!bReturn)
	{
		if( (unsigned long)(buf - lpMpegData + 3) > dwEndPos )
		{
			bReturn = false;
			break;
		}

		if( !bReturn && bufTmp == buf 
			&& is_syncword_mp123(buf) ) //아래 while문을 안타고 무한루프 돌기때문에 추가(add by 박혜숙)
			buf++;

		while (!is_syncword_mp123(buf))
		{
			if( (unsigned long)(buf - lpMpegData + 3) > dwEndPos )
			{
				return false;
			}
			else
			{
				buf++;
			}
		}

		if ((buf[2] & 0xf0)==0) {
			bReturn = false;
			bufTmp = buf; //syncword이고 (buf[2] & 0xf0)값이 0인 경우 무한루프 돌기때문에 추가(add by 박혜숙)
			continue;
			//freeformat = 1;
		} else {
			bReturn = true;
			break;
		}
	}

	if(!bReturn) return bReturn;

	dwStartPos = (unsigned long)(buf - lpMpegData);

	// finding ID3 TAG v1
	buf = lpMpegData + dwEndPos - 128;
	if (memcmp(buf, "TAG", 3) == 0)
	{
		//memcpy(&m_stTag, buf, 128);
		dwEndPos -= 128;
	}

	return bReturn;
}


#endif

