; Inno Setup File
; Bomb - six rooms frontend tools

[Setup]
AppName = Bomb
AppVersion = 0.1.11
DefaultDirName = {pf}\Bomb
ArchitecturesInstallIn64BitMode = x64
ArchitecturesAllowed = x64
SetupLogging = yes
ChangesEnvironment = yes

[Files]
Source: "dist\*"; DestDir: "{app}"
Source: "dist\bomb\*"; DestDir: "{app}\bomb";
Source: "dist\bomb\jar\*"; DestDir: "{app}\bomb\jar";
Source: "dist\distutils\*"; DestDir: "{app}\distutils";
Source: "dist\encodings\*"; DestDir: "{app}\encodings";
Source: "dist\json\*"; DestDir: "{app}\json";
Source: "dist\logging\*"; DestDir: "{app}\logging";
Source: "dist\unittest\*"; DestDir: "{app}\unittest";
Source: "thirdparty\svn\*"; DestDir: "{app}\svn\"; Check: checksvn; AfterInstall: addsvnenv('{app}\svn\');

[Registry]
Root: HKCR; Subkey: "*\Shell\Bomb"; ValueType:expandsz; ValueData: "Bomb"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\Shell\Bomb\command"; ValueType:expandsz; ValueData: "{app}\bomb.exe %1"; Flags: uninsdeletekey

[code]
var
  needsvn: Boolean;


const
  ENV_PATH = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';
  JRE_PATH = 'SOFTWARE\JavaSoft\Java Runtime Environment';
  JDK_PATH = 'SOFTWARE\JavaSoft\Java Development Kit';
  JAVA_VERSION_KEY = 'CurrentVersion';
  JAVA_DOWNLOAD_URL = 'http://www.oracle.com/technetwork/java/javase/downloads/index.html';


{ Add Path To Environment }
procedure addenvpath(path: String);
var
  pathenv: String;
  findpos: Integer;

begin
  RegQueryStringValue(HKEY_LOCAL_MACHINE, ENV_PATH, 'Path', pathenv);
  findpos := Pos(path, pathenv);

  if findpos = 0 then
    begin
      Insert(';', path, 0);
      Insert(path, pathenv, Length(pathenv) + 1);
      Log('new path environment:');
      Log(path);
      RegWriteStringValue(HKEY_LOCAL_MACHINE, ENV_PATH, 'Path', pathenv);
      Log('update environment:');
      Log(pathenv);
    end
   else
    begin
      Insert('already in path env: ', path, 0)
      Log(path)
    end;

end;


{ Check SVN Command Line Clinet Tools }
function scansvn(): Boolean;
var
  svndir, svnbin: String;

begin
  needsvn := True;

  RegQueryStringValue(HKLM32, 'SOFTWARE\TortoiseSVN', 'Directory', svndir);
  RegQueryStringValue(HKLM64, 'SOFTWARE\TortoiseSVN', 'Directory', svndir);

  if svndir <> '' then
    begin
      svnbin := Copy(svndir, 0, Length(svndir));
      Insert('bin\svn.exe', svnbin, Length(svnbin) + 1);
      Log(svnbin)
      if FileExists(svnbin) then
        begin
          needsvn := False;
          Log('does not need svn.')
          svnbin := Copy(svndir, 0, Length(svndir));
          Insert('bin', svnbin, Length(svnbin) + 1);
          addenvpath(svnbin);

        end;
    end;
end;


{ Check JRE or JDK }
function scanjre(): Boolean;
var
  version, javahome, javabin, regpath: String;
  finded: Boolean;
  ErrCode: Integer;

begin
  if RegKeyExists(HKLM32, JRE_PATH) or RegKeyExists(HKLM64, JRE_PATH) then
    begin
      RegQueryStringValue(HKLM32, JRE_PATH, JAVA_VERSION_KEY, version);
      RegQueryStringValue(HKLM64, JRE_PATH, JAVA_VERSION_KEY, version);
      regpath := JRE_PATH;
    end;   

  if RegKeyExists(HKLM32, JDK_PATH) or RegKeyExists(HKLM64, JDK_PATH) then
    begin
      RegQueryStringValue(HKLM32, JDK_PATH, JAVA_VERSION_KEY, version);
      RegQueryStringValue(HKLM64, JDK_PATH, JAVA_VERSION_KEY, version);
      regpath := JDK_PATH;
    end;


  if version <> '' then
    begin
      Log('founded JRE or JDK: ');
      Log(regpath);
      Log(version);
 
      Insert('\', regpath, Length(regpath) + 1);
      Insert(version, regpath, Length(regpath) + 1);

      Log(regpath);

      RegQueryStringValue(HKLM32, regpath, 'JavaHome', javahome);
      RegQueryStringValue(HKLM64, regpath, 'JavaHome', javahome);

      Log(javahome);

      javabin := Copy(javahome, 0, Length(javahome));
      Insert('\bin', javabin, Length(javabin) + 1)
      addenvpath(javabin)
      result := True;

    end
  else
    begin
      Log('JRE or JDK not founded');
      if MsgBox('Java is required. Do you want to download it now ?', mbConfirmation, MB_YESNO) = IDYES then
        ShellExec('open', JAVA_DOWNLOAD_URL, '', '', SW_SHOW, ewNoWait, ErrCode);
      result := False
    end;
end;


{ Check SVN Flag }
function checksvn(): Boolean;
begin
  result := needsvn;
end;


procedure addsvnenv(path: String);
begin
  Log('add svn command line tools directory to environment.');
  addenvpath(ExpandConstant(path));
end;


function InitializeSetup(): Boolean;
begin
  result := scanjre();
  scansvn();
end;

