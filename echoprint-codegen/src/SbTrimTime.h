#ifndef SBTRIMTIME_H
#define SBTRIMTIME_H

#include <stdio.h>


// 반올림 함수
int _round(double number)
{
    return (number >= 0) ? (int)(number + 0.5) : (int)(number - 0.5);
}

// 시간 계산 
// track_duration: 오디오트랙의 길이
// target_duration: 자르고자 하는 윈도우의 길이
// track_offset, target_offset 두개의 지점을 연결하여 자르고자 하는 구간이 결정됨
// track_offset: 오디오트랙에서의 오프셋 지점: 백분률 단위로 계산됨
// target_offset: 자르고자 하는 윈도우에서의 오프셋 지점: 백분률 단위로 계산됨
// ex: 25% 지점 에서  45초: track_offset=0.25 target_offset=0.0 target_duration=45
// ex: 75% 지점 에서 거꾸로 45초: track_offset=0.75 target_offset=1.0 target_duration=45
int trim_time(int track_duration, double track_offset, double target_offset, int target_duration)
{
    double start = 0;
    double duration = 0;
    double joint_point = 0;
    track_duration = (double)track_duration;
    target_duration = (double)target_duration;

    // track_duration 혹은 target_durationd이 0이면 0 리턴
    if((track_duration == 0)||(target_duration == 0))
    {
        return 0;
    }

    // track_duration이 1200초를 초과하는 값인 경우 1200으로 변환
    if(track_duration > 1200000)
    {
        track_duration = 1200000;
    }

    // 시작계산 부분
    if(track_duration <= target_duration)
    {
        start = 0;
        duration = track_duration;
    }
    else
    {
        joint_point = track_duration * track_offset;
        if((joint_point - (target_duration * target_offset)) < 0)
        {
            start = 0;
            duration = target_duration;
        }
        else if((joint_point + (target_duration * (1 - target_offset))) > track_duration)
        {
            start = track_duration - target_duration;
            duration = target_duration;
        }
        else
        {
            start = (track_duration * track_offset) - (target_duration * target_offset);
            duration = target_duration;
        }
    }
    // start, duration 반올림하여 리턴
    start = _round(start);
    duration = _round(duration);
    return start;
}

#endif

