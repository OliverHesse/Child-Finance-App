def CharacterSetCheck(input, charSet):
  for ch in input:
    #check if character is not present in the set
    if ch not in charSet:

      return False

  return True


def ExcludeSet(input, charSet):
  for ch in input:
    #checkk if character is present in set
    if ch in charSet:

      return False

  return True


def isDate(input):
  values = input.split("/")
  #epect 3 items day,month,year
  if len(values) != 3:
    return False
  for item in values:
    try:
      int(item)
    except:
      return False
  #now check ranges
  #a month -> max day map
  #i will assume leap year for max febuary
  daysMap = {
      1: 31,
      2: 28,
      3: 31,
      4: 30,
      5: 31,
      6: 30,
      7: 31,
      8: 31,
      9: 30,
      10: 31,
      11: 30,
      12: 31
  }
  #check if month is in map
  #can combine into one if statement
  leapYear = int(values[2]) % 4 == 0
  if int(values[1]) in daysMap:
    end = daysMap[int(values[1])]
    if leapYear == True and int(values[1]) == 2:
      end += 1
    c2 = int(values[0]) < 1 or int(values[0]) > end
    c3 = int(values[2]) < 1 or int(values[2]) > 9999

    if c2 or c3:
      return False
  return True


def inRange(start, end, input, isInclusive=True):
  #make sure it is not to small
  if input < start:
    return False

  #check value against upper range inclusivly or exclusivly
  condition1 = isInclusive == True and input > end
  condition2 = isInclusive == False and input >= end
  if condition1 or condition2:
    return False
  return True



