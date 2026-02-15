# https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853

[Skip to main content](https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853#main)

![Raymond Chen](https://devblogs.microsoft.com/oldnewthing/wp-content/uploads/sites/38/2019/02/RaymondChen_5in-150x150.jpg)

[Raymond Chen](https://devblogs.microsoft.com/oldnewthing/author/oldnewthing)

Your DllMain function runs inside the loader lock,
one of the few times the OS lets you run code while one
of its internal locks is held.
This means that you must be extra careful not to violate
a lock hierarchy in your DllMain; otherwise, you
are asking for a deadlock.

(You do have a
[lock hierarchy](http://www.osr.com/ddk/ddtools/dv_8pkj.htm) in your DLL, right?)

The loader lock is taken by any function that needs to
access the list of DLLs loaded into the process.
This includes functions like GetModuleHandle
and GetModuleFileName.
If your DllMain enters a critical section or waits on
a synchronization object, and that critical section or
synchronization object is owned by some code that is
in turn waiting for the loader lock, you just created a deadlock:

```
// global variable
CRITICAL_SECTION g_csGlobal;
// some code somewhere
EnterCriticalSection(&g_csGlobal);
... GetModuleFileName(MyInstance, ..);
LeaveCriticalSection(&g_csGlobal);
BOOL WINAPI
DllMain(HINSTANCE hinstDLL, DWORD fdwReason,
        LPVOID lpvReserved)
{
  switch (fdwReason) {
  ...
  case DLL_THREAD_DETACH:
   EnterCriticalSection(&g_csGlobal);
   ...
  }
  ...
}
```

Now imagine that some thread is happily executing the first
code fragment and enters g\_csGlobal, then
gets pre-empty. During this time, another thread exits.
This enters the loader lock and sends out
DLL\_THREAD\_DETACH messages while the loader lock is still held.

You receive the DLL\_THREAD\_DETACH and attempt to enter your DLL’s
g\_csGlobal. This blocks on the first thread, who owns the
critical section. That thread then resumes execution and calls
GetModuleFileName. This function requires the loader lock
(since it’s accessing the list of DLLs loaded into the process),
so it blocks, since the loader lock is owned by somebody else.

Now you have a deadlock:

- g\_cs owned by first thread, waiting on loader lock.

- Loader lock owned by second thread, waiting on g\_cs.


I have seen this happen. It’s not pretty.

Moral of the story: Respect the loader lock.
Include it in your lock hierarchy rules if you take
any locks in your DllMain.

Category

[Old New Thing](https://devblogs.microsoft.com/oldnewthing/category/oldnewthing)

Topics

[Code](https://devblogs.microsoft.com/oldnewthing/tag/code)

Share

- [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853)
- [Share on X](https://twitter.com/intent/tweet?url=https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853&text=Another%20reason%20not%20to%20do%20anything%20scary%20in%20your%20DllMain:%20Inadvertent%20deadlock)
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853)

## Author

![Raymond Chen](https://devblogs.microsoft.com/oldnewthing/wp-content/uploads/sites/38/2019/02/RaymondChen_5in-150x150.jpg)

[Raymond Chen](https://devblogs.microsoft.com/oldnewthing/author/oldnewthing)

Raymond has been involved in the evolution of Windows for more than 30 years. In 2003, he began a Web site known as The Old New Thing which has grown in popularity far beyond his wildest imagination, a development which still gives him the heebie-jeebies. The Web site spawned a book, coincidentally also titled The Old New Thing (Addison Wesley 2007). He occasionally appears on the Windows Dev Docs Twitter account to tell stories which convey no useful information.

## 0 comments

Discussion is closed.

[Code of Conduct](https://aka.ms/msftqacodeconduct)

## Stay informed

Get notified when new posts are published.

Email \*

Country/Region \*Select...United StatesAfghanistanÅland IslandsAlbaniaAlgeriaAmerican SamoaAndorraAngolaAnguillaAntarcticaAntigua and BarbudaArgentinaArmeniaArubaAustraliaAustriaAzerbaijanBahamasBahrainBangladeshBarbadosBelarusBelgiumBelizeBeninBermudaBhutanBoliviaBonaireBosnia and HerzegovinaBotswanaBouvet IslandBrazilBritish Indian Ocean TerritoryBritish Virgin IslandsBruneiBulgariaBurkina FasoBurundiCabo VerdeCambodiaCameroonCanadaCayman IslandsCentral African RepublicChadChileChinaChristmas IslandCocos (Keeling) IslandsColombiaComorosCongoCongo (DRC)Cook IslandsCosta RicaCôte dIvoireCroatiaCuraçaoCyprusCzechiaDenmarkDjiboutiDominicaDominican RepublicEcuadorEgyptEl SalvadorEquatorial GuineaEritreaEstoniaEswatiniEthiopiaFalkland IslandsFaroe IslandsFijiFinlandFranceFrench GuianaFrench PolynesiaFrench Southern TerritoriesGabonGambiaGeorgiaGermanyGhanaGibraltarGreeceGreenlandGrenadaGuadeloupeGuamGuatemalaGuernseyGuineaGuinea-BissauGuyanaHaitiHeard Island and McDonald IslandsHondurasHong Kong SARHungaryIcelandIndiaIndonesiaIraqIrelandIsle of ManIsraelItalyJamaicaJan MayenJapanJerseyJordanKazakhstanKenyaKiribatiKoreaKosovoKuwaitKyrgyzstanLaosLatviaLebanonLesothoLiberiaLibyaLiechtensteinLithuaniaLuxembourgMacau SARMadagascarMalawiMalaysiaMaldivesMaliMaltaMarshall IslandsMartiniqueMauritaniaMauritiusMayotteMexicoMicronesiaMoldovaMonacoMongoliaMontenegroMontserratMoroccoMozambiqueMyanmarNamibiaNauruNepalNetherlandsNew CaledoniaNew ZealandNicaraguaNigerNigeriaNiueNorfolk IslandNorth MacedoniaNorthern Mariana IslandsNorwayOmanPakistanPalauPalestinian AuthorityPanamaPapua New GuineaParaguayPeruPhilippinesPitcairn IslandsPolandPortugalPuerto RicoQatarRéunionRomaniaRwandaSabaSaint BarthélemySaint Kitts and NevisSaint LuciaSaint MartinSaint Pierre and MiquelonSaint Vincent and the GrenadinesSamoaSan MarinoSão Tomé and PríncipeSaudi ArabiaSenegalSerbiaSeychellesSierra LeoneSingaporeSint EustatiusSint MaartenSlovakiaSloveniaSolomon IslandsSomaliaSouth AfricaSouth Georgia and South Sandwich IslandsSouth SudanSpainSri LankaSt HelenaAscensionTristan da CunhaSurinameSvalbardSwedenSwitzerlandTaiwanTajikistanTanzaniaThailandTimor-LesteTogoTokelauTongaTrinidad and TobagoTunisiaTurkeyTurkmenistanTurks and Caicos IslandsTuvaluU.S. Outlying IslandsU.S. Virgin IslandsUgandaUkraineUnited Arab EmiratesUnited KingdomUruguayUzbekistanVanuatuVatican CityVenezuelaVietnamWallis and FutunaYemenZambiaZimbabwe

I would like to receive the The Old New Thing Newsletter. [Privacy Statement.](https://go.microsoft.com/fwlink/?LinkId=521839)

Subscribe

Follow this blog

[twitter](https://twitter.com/ChenCravat "twitter")[![youtube](https://devblogs.microsoft.com/oldnewthing/wp-content/themes/devblogs-evo/images/social-icons/youtube.svg)](https://www.youtube.com/playlist?list=PLlrxD0HtieHge3_8Dm48C0Ns61I6bHThc "youtube")[GitHub](https://github.com/oldnewthing "GitHub")[RSS Feed](https://devblogs.microsoft.com/oldnewthing/feed/ "RSS Feed")

# Insert/edit link

Close

Enter the destination URL

URL

Link Text

Open link in a new tab

Or link to existing content

Search

_No search term specified. Showing recent items._ _Search or use up and down arrow keys to select an item._

Cancel

[Back to top](https://devblogs.microsoft.com/oldnewthing/20040128-00/?p=40853#page "Back to top")

×

Notifications